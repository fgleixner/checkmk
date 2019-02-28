// watest.cpp : This file contains the 'main' function. Program execution begins
// and ends there.
//
#include "pch.h"

#include <time.h>

#include <chrono>
#include <filesystem>
#include <future>
#include <string_view>

#include "common/cfg_info.h"

#include "read_file.h"

#include "cfg.h"
#include "cfg_details.h"

#include "cma_core.h"

#include "providers/mrpe.h"

/*
Typic output:

<<<mrpe>>>
(mode.com) Console 0 Status von Gerät CON: \1 --------------------- \1
Codepage:        437 (chcp.com) sk 1 Geben Sie das Kennwort für "sk" ein:
*/

namespace cma::provider {  // to become friendly for wtools classes
TEST(SectionProviderMrpe, Construction) {
    MrpeProvider mrpe;
    EXPECT_EQ(mrpe.getUniqName(), cma::section::kMrpe);
    EXPECT_EQ(mrpe.accu_.size(), 0);
    EXPECT_EQ(mrpe.checks_.size(), 0);
    EXPECT_EQ(mrpe.entries_.size(), 0);
    EXPECT_EQ(mrpe.includes_.size(), 0);
    auto out = mrpe.makeBody();
    EXPECT_TRUE(out.empty());
    mrpe.accu_.push_back('a');
    mrpe.accu_.push_back('\n');
    out = mrpe.generateContent(cma::section::kUseEmbeddedName);
    // very simple : concatenate accu_ and makeHeader
    EXPECT_EQ(out, "<<<mrpe>>>\na\n") << out;
}

void replaceYamlSeq(const std::string Group, const std::string SeqName,
                    std::vector<std::string> Vec) {
    YAML::Node Yaml = cma::cfg::GetLoadedConfig();
    for (size_t i = 0; i < Yaml[Group][SeqName].size(); i++)
        Yaml[Group][SeqName].remove(0);

    Yaml[Group][SeqName].reset();

    for (auto& str : Vec) {
        Yaml[Group][SeqName].push_back(str);
    }
}

TEST(SectionProviderMrpe, SmallApi) {
    std::string s = "a\rb\n\n";
    FixCrCnForMrpe(s);
    EXPECT_EQ(s, "a b\1\1");

    {
        auto [user, path] =
            cma::provider::parseIncludeEntry("sk = @data\\mrpe_checks.cfg");
        EXPECT_EQ(user, "sk");
        EXPECT_EQ(path.u8string(),
                  wtools::ConvertToUTF8(cma::cfg::GetUserDir()) + "\\" +
                      "mrpe_checks.cfg");
    }
}

TEST(SectionProviderMrpe, ConfigLoad) {
    using namespace cma::cfg;
    cma::OnStart(cma::kTest);
    ON_OUT_OF_SCOPE(cma::OnStart(cma::kTest););
    MrpeProvider mrpe;
    EXPECT_EQ(mrpe.getUniqName(), cma::section::kMrpe);
    auto yaml = GetLoadedConfig();
    ASSERT_TRUE(yaml.IsMap());

    auto mrpe_yaml_optional = GetGroup(yaml, groups::kMrpe);
    ASSERT_TRUE(mrpe_yaml_optional.has_value());
    {
        auto& mrpe_cfg = mrpe_yaml_optional.value();

        ASSERT_TRUE(GetVal(mrpe_cfg, vars::kEnabled, false));
        auto entries = GetArray<std::string>(mrpe_cfg, vars::kMrpeConfig);
        ASSERT_EQ(entries.size(), 3)
            << "check that yml is ok";  // include and check
    }

    replaceYamlSeq(
        groups::kMrpe, vars::kMrpeConfig,
        {"check = Console 'c:\\windows\\system32\\mode.com' CON CP /STATUS",
         "include sk = @data\\mrpe_checks.cfg",  // reference
         "Include=@data\\mrpe_checks.cfg",       // valid without space
         "includes = @data\\mrpe_checks.cfg",    // invalid
         "includ = @data\\mrpe_checks.cfg",      // invalid
         "chck = Console 'c:\\windows\\system32\\mode.com' CON CP /STATUS",  // invalid
         "check = 'c:\\windows\\system32\\mode.com' CON CP /STATUS"});  // valid

    auto strings = GetArray<std::string>(groups::kMrpe, vars::kMrpeConfig);
    EXPECT_EQ(strings.size(), 7);
    mrpe.parseConfig();
    ASSERT_EQ(mrpe.includes_.size(), 2);
    mrpe.parseConfig();
    ASSERT_EQ(mrpe.includes_.size(), 2);
    EXPECT_EQ(mrpe.includes_[0], "sk = @data\\mrpe_checks.cfg");
    EXPECT_EQ(mrpe.includes_[1], "=@data\\mrpe_checks.cfg");
    ASSERT_EQ(mrpe.checks_.size(), 2);
    EXPECT_EQ(mrpe.checks_[0],
              "Console 'c:\\windows\\system32\\mode.com' CON CP /STATUS");
    EXPECT_EQ(mrpe.checks_[1],
              "'c:\\windows\\system32\\mode.com' CON CP /STATUS");

    mrpe.addParsedConfig();
    EXPECT_EQ(mrpe.includes_.size(), 2);
    EXPECT_EQ(mrpe.checks_.size(), 2);
    EXPECT_EQ(mrpe.entries_.size(), 3);
}  // namespace cma::provider

TEST(SectionProviderMrpe, Run) {
    using namespace cma::cfg;
    cma::OnStart(cma::kTest);
    ON_OUT_OF_SCOPE(cma::OnStart(cma::kTest););
    MrpeProvider mrpe;
    EXPECT_EQ(mrpe.getUniqName(), cma::section::kMrpe);
    auto yaml = GetLoadedConfig();
    ASSERT_TRUE(yaml.IsMap());

    auto mrpe_yaml_optional = GetGroup(yaml, groups::kMrpe);
    ASSERT_TRUE(mrpe_yaml_optional.has_value());
    {
        auto& mrpe_cfg = mrpe_yaml_optional.value();

        ASSERT_TRUE(GetVal(mrpe_cfg, vars::kEnabled, false));
        auto entries = GetArray<std::string>(mrpe_cfg, vars::kMrpeConfig);
        ASSERT_EQ(entries.size(), 3)
            << "check that yml is ok";  // include and check
    }

    replaceYamlSeq(
        groups::kMrpe, vars::kMrpeConfig,
        {
            "check = Codepage 'c:\\windows\\system32\\chcp.com'",
            "check = Console 'c:\\windows\\system32\\mode.com' CON CP /STATUS",
        });

    auto strings = GetArray<std::string>(groups::kMrpe, vars::kMrpeConfig);
    EXPECT_EQ(strings.size(), 2);
    mrpe.parseConfig();
    ASSERT_EQ(mrpe.includes_.size(), 0);
    ASSERT_EQ(mrpe.checks_.size(), 2);

    mrpe.addParsedConfig();
    EXPECT_EQ(mrpe.entries_.size(), 2);
    mrpe.updateSectionStatus();
    auto accu = mrpe.accu_;
    ASSERT_TRUE(!accu.empty());
    auto table = cma::tools::SplitString(accu, "\n");
    ASSERT_EQ(table.size(), 2);

    auto& e0 = mrpe.entries_[0];
    {
        auto hdr =
            fmt::format("({})", e0.exe_name_) + " " + e0.description_ + " 0";
        EXPECT_TRUE(table[0].find(hdr) == 0);
    }
    auto& e1 = mrpe.entries_[1];
    {
        auto hdr =
            fmt::format("({})", e1.exe_name_) + " " + e1.description_ + " 0";
        EXPECT_TRUE(table[1].find(hdr) == 0);
    }
}  // namespace cma::provider

}  // namespace cma::provider
