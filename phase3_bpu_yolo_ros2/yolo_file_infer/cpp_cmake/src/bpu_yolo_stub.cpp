// ============================================================================
// File:        bpu_yolo_stub.cpp
// Project:     d-robotics (ParkCircus Productions)
// License:     MIT
// Description: Phase 3 file-based BPU YOLO stub emitting DeviceId & Waqt JSON.
// ============================================================================

#include <chrono>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <unistd.h>

namespace {

std::string resolve_device_id() {
    const char* env_host = std::getenv("WIFI_HOSTNAME_DEFAULT");
    if (env_host != nullptr && *env_host != '\0') {
        return std::string(env_host);
    }
    char buf[256] = {0};
    if (gethostname(buf, sizeof(buf) - 1) == 0 && buf[0] != '\0') {
        return std::string(buf);
    }
    return "unknown-device";
}

std::string current_waqt() {
    auto now = std::chrono::system_clock::now();
    std::time_t tt = std::chrono::system_clock::to_time_t(now);
    std::tm tm_local{};
    localtime_r(&tt, &tm_local);
    std::ostringstream oss;
    oss << std::put_time(&tm_local, "%Y-%m-%dT%H:%M:%S");
    return oss.str();
}

std::string json_escape(const std::string& s) {
    std::ostringstream oss;
    for (char c : s) {
        switch (c) {
            case '\\': oss << "\\\\"; break;
            case '"':  oss << "\\\""; break;
            case '\n': oss << "\\n"; break;
            case '\r': oss << "\\r"; break;
            case '\t': oss << "\\t"; break;
            default:   oss << c; break;
        }
    }
    return oss.str();
}

bool get_file_size(const std::string& path, long long& out_bytes) {
    std::ifstream ifs(path, std::ios::binary | std::ios::ate);
    if (!ifs.is_open()) {
        return false;
    }
    out_bytes = static_cast<long long>(ifs.tellg());
    return out_bytes >= 0;
}

}  // namespace

int main(int argc, char* argv[]) {
    std::string input_path;
    std::string model_path;
    std::string output_path;
    bool dry_run = false;

    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        if (arg == "--input" && i + 1 < argc) {
            input_path = argv[++i];
        } else if (arg == "--model" && i + 1 < argc) {
            model_path = argv[++i];
        } else if (arg == "--output" && i + 1 < argc) {
            output_path = argv[++i];
        } else if (arg == "--dry-run") {
            dry_run = true;
        }
    }

    const std::string device_id = resolve_device_id();
    const std::string waqt = current_waqt();

    if (input_path.empty()) {
        std::cerr << "{\n"
                  << "  \"DeviceId\": \"" << json_escape(device_id) << "\",\n"
                  << "  \"Waqt\": \"" << json_escape(waqt) << "\",\n"
                  << "  \"status\": \"error\",\n"
                  << "  \"error\": \"Missing required --input argument\"\n"
                  << "}\n";
        return 1;
    }

    long long input_bytes = 0;
    if (!get_file_size(input_path, input_bytes)) {
        std::cerr << "{\n"
                  << "  \"DeviceId\": \"" << json_escape(device_id) << "\",\n"
                  << "  \"Waqt\": \"" << json_escape(waqt) << "\",\n"
                  << "  \"status\": \"error\",\n"
                  << "  \"error\": \"Cannot open input file: " << json_escape(input_path) << "\"\n"
                  << "}\n";
        return 1;
    }

#ifdef BPU_STUB_MODE
    const bool stub_compiled = true;
#else
    const bool stub_compiled = false;
#endif
    const bool stub_active = dry_run || stub_compiled;

    std::ostringstream json;
    json << "{\n"
         << "  \"DeviceId\": \"" << json_escape(device_id) << "\",\n"
         << "  \"Waqt\": \"" << json_escape(waqt) << "\",\n"
         << "  \"status\": \"ok\",\n"
         << "  \"stub_mode\": " << (stub_active ? "true" : "false") << ",\n"
         << "  \"input_path\": \"" << json_escape(input_path) << "\",\n"
         << "  \"input_bytes\": " << input_bytes << ",\n"
         << "  \"model_path\": \"" << json_escape(model_path) << "\",\n"
         << "  \"detections\": [\n"
         << "    {\"label\": \"stub_object\", \"score\": 0.82, \"bbox\": [32, 40, 180, 260]}\n"
         << "  ]\n"
         << "}\n";

    if (!output_path.empty()) {
        std::ofstream ofs(output_path, std::ios::binary);
        if (ofs.is_open()) {
            ofs << json.str();
        }
    }

    std::cout << json.str();
    return 0;
}
