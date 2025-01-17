#!/usr/bin/env python3
# Copyright (C) 2023 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from datetime import datetime
from pathlib import Path

import pytest
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from cmk.utils.crypto import HashAlgorithm
from cmk.utils.crypto.certificate import (
    CertificateWithPrivateKey,
    InvalidExpiryError,
    InvalidPEMError,
    InvalidSignatureError,
    PersistedCertificateWithPrivateKey,
    RsaPrivateKey,
    Signature,
    WrongPasswordError,
)
from cmk.utils.crypto.password import Password

# this is the same as in testlib.certs
FROZEN_NOW = datetime(2023, 1, 1, 8, 0, 0)


def test_generate_self_signed(self_signed_cert: CertificateWithPrivateKey) -> None:
    assert (
        self_signed_cert.public_key
        == self_signed_cert.certificate.public_key
        == self_signed_cert.private_key.public_key
    )

    self_signed_cert.certificate.verify_is_signed_by(self_signed_cert.certificate)

    assert "TestGenerateSelfSigned" == self_signed_cert.certificate.common_name
    assert "Checkmk Site" in self_signed_cert.certificate.organization_name


@pytest.mark.parametrize(
    "time_offset,allowed_drift,expectation",
    [
        (
            relativedelta(hours=-5),  # It's 5 hours BEFORE cert creation.
            None,  # The default 2 hours slack is not enough.
            pytest.raises(InvalidExpiryError, match="not yet valid"),
        ),
        (relativedelta(hours=+5), None, pytest.raises(InvalidExpiryError, match="expired")),
        (
            # It's now 5 hours after cert creation, so the cert has expired 3 hours ago.
            relativedelta(hours=+5),
            relativedelta(hours=+5),  # But we allow 5 hours drift.
            does_not_raise(),
        ),
        (relativedelta(minutes=+10), None, does_not_raise()),
    ],
)
def test_verify_expiry(
    self_signed_cert: CertificateWithPrivateKey,
    time_offset: relativedelta,
    allowed_drift: relativedelta,
    expectation: AbstractContextManager,
) -> None:
    # time_offset is the time difference to (mocked) certificate creation
    # allowed_drift is the tolerance parameter of verify_expiry (defaults to 2 hours for None)
    #
    # We assume the cert is valid from FROZEN_NOW til FROZEN_NOW + 2 hours.
    #
    with freeze_time(FROZEN_NOW + time_offset):
        with expectation:
            self_signed_cert.certificate.verify_expiry(allowed_drift)


@pytest.mark.parametrize(
    "when,expected_days_remaining",
    [
        (relativedelta(seconds=0), 0),  # in 2 hours
        (relativedelta(days=-1), 1),  # yesterday it was valid for another day
        (relativedelta(months=-12), 365),  # 2022 was not a leap year
        (relativedelta(hours=+2), 0),  # expires right now
        (relativedelta(hours=+4), -1),  # today but rounded "down" to a day ago
    ],
)
def test_days_til_expiry(
    self_signed_cert: CertificateWithPrivateKey,
    when: relativedelta,
    expected_days_remaining: relativedelta,
) -> None:
    with freeze_time(FROZEN_NOW + when):
        assert self_signed_cert.certificate.days_til_expiry() == expected_days_remaining


def test_write_and_read(tmp_path: Path, self_signed_cert: CertificateWithPrivateKey) -> None:
    cert_path = tmp_path / "cert.crt"
    key_path = tmp_path / "key.pem"
    password = Password("geheim")

    PersistedCertificateWithPrivateKey.persist(self_signed_cert, cert_path, key_path, password)

    assert key_path.read_bytes().splitlines()[0] == b"-----BEGIN ENCRYPTED PRIVATE KEY-----"
    assert cert_path.read_bytes().splitlines()[0] == b"-----BEGIN CERTIFICATE-----"

    loaded = PersistedCertificateWithPrivateKey.read_files(cert_path, key_path, password)

    assert loaded.certificate.serial_number == self_signed_cert.certificate.serial_number

    # mypy doesn't find most attributes of cryptography's RSAPrivateKey as it seems
    loaded_nums = loaded.private_key._key.private_numbers()  # type: ignore[attr-defined]
    orig_nums = self_signed_cert.private_key._key.private_numbers()  # type: ignore[attr-defined]
    assert loaded_nums == orig_nums


def test_serialize_rsa_key(tmp_path: Path) -> None:
    key = RsaPrivateKey.generate(512)

    pem_plain = key.dump_pem(None)
    assert pem_plain.bytes.startswith(b"-----BEGIN PRIVATE KEY-----")

    loaded_plain = RsaPrivateKey.load_pem(pem_plain)
    assert loaded_plain._key.private_numbers() == key._key.private_numbers()  # type: ignore[attr-defined]

    pem_enc = key.dump_pem(Password("verysecure"))
    assert pem_enc.bytes.startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-----")

    with pytest.raises(WrongPasswordError):
        RsaPrivateKey.load_pem(pem_enc, Password("wrong"))

    loaded_enc = RsaPrivateKey.load_pem(pem_enc, Password("verysecure"))
    assert loaded_enc._key.private_numbers() == key._key.private_numbers()  # type: ignore[attr-defined]


@pytest.mark.parametrize("data", [b"", b"test", b"\0\0\0", "sign here: 📝".encode("utf-8")])
def test_verify_rsa_key(data: bytes) -> None:
    private_key = RsaPrivateKey.generate(1024)
    signed = private_key.sign_data(data)

    private_key.public_key.verify(signed, data, HashAlgorithm.Sha512)

    with pytest.raises(InvalidSignatureError):
        private_key.public_key.verify(Signature(b"nope"), data, HashAlgorithm.Sha512)


def test_loading_combined_file_content(self_signed_cert: CertificateWithPrivateKey) -> None:
    pw = Password("unittest")
    with pytest.raises(InvalidPEMError, match="Could not find certificate"):
        CertificateWithPrivateKey.load_combined_file_content("", None)

    with pytest.raises(InvalidPEMError, match="Unable to load certificate."):
        CertificateWithPrivateKey.load_combined_file_content(
            "-----BEGIN CERTIFICATE-----a-----END CERTIFICATE-----", None
        )

    file_content = self_signed_cert.certificate.dump_pem().str
    with pytest.raises(InvalidPEMError, match="Could not find private key"):
        CertificateWithPrivateKey.load_combined_file_content(file_content, None)
    with pytest.raises(InvalidPEMError, match="Could not find encrypted private key"):
        CertificateWithPrivateKey.load_combined_file_content(file_content, pw)

    assert (
        CertificateWithPrivateKey.load_combined_file_content(
            file_content + "\n" + self_signed_cert.private_key.dump_pem(None).str, None
        )
        .certificate.dump_pem()
        .str
        == self_signed_cert.certificate.dump_pem().str
    )
    assert (
        CertificateWithPrivateKey.load_combined_file_content(
            file_content + "\n" + self_signed_cert.private_key.dump_pem(pw).str, pw
        )
        .certificate.dump_pem()
        .str
        == self_signed_cert.certificate.dump_pem().str
    )
