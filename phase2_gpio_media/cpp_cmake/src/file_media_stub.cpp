// ============================================================================
// File:        file_media_stub.cpp
// Project:     d-robotics (ParkCircus Productions)
// License:     MIT
// Version:     0.2.0
// Description: Phase 2 C++ file-based media pipeline entry point supporting
//              both hardware/target builds and non-hardware stub builds.
// ============================================================================

#include "stub_hal.hpp"

#include <chrono>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <unistd.h>

namespace fs = std::filesystem;

namespace rdkx3::phase2 {

std::string current_utc_waqt() {
    const auto now = std::chrono::system_clock::now();
    const std::time_t tt = std::chrono::system_clock::to_time_t(now);
    std::tm tm_utc{};
#if defined(_WIN32)
    gmtime_s(&tm_utc, &tt);
#else
    gmtime_r(&tt, &tm_utc);
#endif
    std::ostringstream oss;
    oss << std::put_time(&tm_utc, "%Y-%m-%dT%H:%M:%S");
    return oss.str();
}

std::string default_device_id() {
    char buf[256]{};
    if (gethostname(buf, sizeof(buf)) == 0) {
        std::string host(buf);
        const auto dot = host.find('.');
        if (dot != std::string::npos) {
            host = host.substr(0, dot);
        }
        if (!host.empty()) {
            return host;
        }
    }
    return "rdkx3-node";
}

bool process_media_file(const std::string& input_path,
                        const std::string& output_path,
                        MediaFrameInfo& out_info) {
    std::error_code ec;
    if (!fs::exists(input_path, ec) || !fs::is_regular_file(input_path, ec)) {
        std::cerr << "Error: input media file does not exist or is not a regular file: "
                  << input_path << "\n";
        return false;
    }

    const auto file_size = fs::file_size(input_path, ec);
    if (ec) {
        std::cerr << "Error: unable to stat input media file: " << input_path << "\n";
        return false;
    }

#if defined(RDKX3_STUB_HARDWARE) && (RDKX3_STUB_HARDWARE == 1)
    out_info.stub_mode = true;
#else
    out_info.stub_mode = false;
#endif

    out_info.input_path = input_path;
    out_info.output_path = output_path;
    out_info.width = 1280;
    out_info.height = 720;
    out_info.frame_index = 1;

    if (!output_path.empty()) {
        const fs::path out_p(output_path);
        if (out_p.has_parent_path()) {
            fs::create_directories(out_p.parent_path(), ec);
        }
        std::ofstream ofs(output_path, std::ios::binary | std::ios::trunc);
        if (!ofs.is_open()) {
            std::cerr << "Error: failed to open output file: " << output_path << "\n";
            return false;
        }
        ofs << "# Phase 2 media pipeline stub/output artifact\n"
            << "DeviceId=" << default_device_id() << "\n"
            << "Waqt=" << current_utc_waqt() << "\n"
            << "Input=" << input_path << "\n"
            << "InputBytes=" << file_size << "\n"
            << "StubMode=" << (out_info.stub_mode ? "true" : "false") << "\n";
    }

    return true;
}

}  // namespace rdkx3::phase2

namespace {

void print_usage(const char* prog) {
    std::cerr << "Usage: " << prog
              << " --input <image_or_video_path> [--output <artifact_path>] [--device-id <id>]\n";
}

}  // namespace

int main(int argc, char* argv[]) {
    std::string input_path;
    std::string output_path;
    std::string device_id = rdkx3::phase2::default_device_id();

    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        if (arg == "--input" && i + 1 < argc) {
            input_path = argv[++i];
        } else if (arg == "--output" && i + 1 < argc) {
            output_path = argv[++i];
        } else if (arg == "--device-id" && i + 1 < argc) {
            device_id = argv[++i];
        } else if (arg == "--help" || arg == "-h") {
            print_usage(argv[0]);
            return 0;
        } else {
            print_usage(argv[0]);
            return 1;
        }
    }

    if (input_path.empty()) {
        print_usage(argv[0]);
        return 1;
    }

    rdkx3::phase2::MediaFrameInfo info{};
    if (!rdkx3::phase2::process_media_file(input_path, output_path, info)) {
        return 1;
    }

    std::cout << "{\n"
              << "  \"DeviceId\": \"" << device_id << "\",\n"
              << "  \"Waqt\": \"" << rdkx3::phase2::current_utc_waqt() << "\",\n"
              << "  \"input_path\": \"" << info.input_path << "\",\n"
              << "  \"output_path\": \"" << info.output_path << "\",\n"
              << "  \"stub_mode\": " << (info.stub_mode ? "true" : "false") << ",\n"
              << "  \"status\": \"ok\"\n"
              << "}\n";

    return 0;
}
