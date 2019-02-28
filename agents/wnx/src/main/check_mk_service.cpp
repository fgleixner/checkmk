
// check_mk_service.cpp : This file contains ONLY the 'main' function.

// Precompiled
#include <pch.h>
// system C
// system C++
#include <filesystem>
#include <iostream>
#include <string>

#include "yaml-cpp/yaml.h"

// Project
#include "service_api.h"
#include "windows_service_api.h"

// Personal
#include "check_mk_service.h"

#include "cfg.h"
#include "logger.h"

std::filesystem::path G_ProjectPath = PROJECT_DIR_CMK_SERVICE;

// print short info about usage plus potential comment about error
static void ServiceUsage(const std::wstring &Comment) {
    using namespace cma::cmdline;
    if (Comment != L"") {
        printf("Error: %ls\n", Comment.c_str());
    }
    printf(
        "Usage:\n\t%s.exe <%ls|%ls|%ls|%ls|%ls|%ls|%ls <inifile> [yamlfile]>\n"
        "\t%-10ls - install as a service\n"
        "\t%-10ls - remove service\n"
        "\t%-10ls - legacy test\n"
        "\t%-10ls - short test\n"
        "\t%-10ls - usage\n"
        "\t%-10ls - exec as app\n"
        "\t%-10ls - convert INI file into the YML\n",
        kServiceExeName,  // service name from th project definitions
        // first Row
        kInstallParam, kRemoveParam, kLegacyTestParam, kTestParam, kHelpParam,
        kExecParam, kCvtParam,
        // second row
        kInstallParam, kRemoveParam, kLegacyTestParam, kTestParam, kHelpParam,
        kExecParam, kCvtParam);
}

namespace cma {
bool G_Service = false;
StartTypes AppDefaultType() {
    return G_Service ? StartTypes::kService : StartTypes::kExe;
}

// Command Lines
// -cvt watest/CheckMK/Agent/check_mk.test.ini
//

// we want to test main function too.
// so we have main, but callable
int MainFunction(int argc, wchar_t **Argv) {
    // check for invalid parameters count
    using namespace std::chrono;
    using namespace cma::install;
    if (argc == 1) {
        XLOG::l.i("service to run");
        using namespace cma::srv;
        G_Service = true;
        cma::OnStartApp();  // path from service
        ON_OUT_OF_SCOPE(cma::OnExit());
        return ServiceAsService(1000ms, [](const void *) {
            // optional commands listed here
            // ********
            // 1. Auto Update when  msi file is located by specified address
            CheckForUpdateFile(kDefaultMsiFileName, GetMsiUpdateDirectory(),
                               UpdateType::kMsiExecQuiet, true);
            return true;
        });
    }

    std::wstring param(Argv[1]);

    if (0) {
        // this code is enabled only during testing and debugging
        auto path = G_ProjectPath;
        for (;;) {
            auto yml_test_file =
                G_ProjectPath / "data" / "check_mk.example.yml";
            try {
                YAML::Node config = YAML::LoadFile(yml_test_file.u8string());
            } catch (const std::exception &e) {
                XLOG::l(XLOG_FLINE + " exception %s", e.what());
            } catch (...) {
                XLOG::l(XLOG::kBp)(XLOG_FLINE + " exception bad");
            }
        }
    }

    cma::OnStartApp();  // path from EXE
    using namespace cma::cmdline;
    if (param == kInstallParam) {
        XLOG::l(XLOG::kStdio | XLOG::kInfo)("service to INSTALL");
        return cma::srv::InstallMainService();
    } else if (param == kRemoveParam) {
        XLOG::l(XLOG::kStdio | XLOG::kInfo)("service to REMOVE");
        return cma::srv::RemoveMainService();
    } else if (param == kTestParam) {
        std::wstring param = argc > 2 ? Argv[2] : L"";
        return cma::srv::TestMainService(param);
    } else if (param == kLegacyTestParam) {
        return cma::srv::TestMainService(L"legacy");
    } else if (param == kExecParam) {
        return cma::srv::ExecMainService();
    } else if (param == kSkypeParam) {
        return cma::srv::ExecSkypeTest();
    } else if (param == kCvtParam && argc > 2) {
        std::wstring ini = argc > 2 ? Argv[2] : L"";
        std::wstring yml = argc > 3 ? Argv[3] : L"";
        return cma::srv::ExecCvtIniYaml(ini, yml, true);
    } else if (param == kHelpParam) {
        ServiceUsage(std::wstring(L""));
        return 0;
    } else {
        ServiceUsage(std::wstring(L"Provided Parameter \"") + param +
                     L"\" is not allowed");
        return 2;
    }

    return 0;
}
}  // namespace cma

#if !defined(CMK_TEST)
// This is our main. PLEASE, do not add code here
int wmain(int argc, wchar_t **Argv) { return cma::MainFunction(argc, Argv); }
#endif
