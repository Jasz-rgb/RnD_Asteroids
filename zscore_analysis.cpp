#include "zscore_analysis.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <cmath>
#include <map>
#include <algorithm>
#include <numeric>
#include <vector>

namespace fs = std::filesystem;

const std::string MANUAL_DIR = "results/manual";
const std::string REAL_DIR = "results/real";
const std::string OUTPUT_DIR = "results/zscore";
const double Z_THRESHOLD = 3.0;

static double magnitude(double x, double y, double z) {
    return std::sqrt(x * x + y * y + z * z);
}

// =====================
// LOAD CSV
// =====================
std::map<std::string, DataRow> loadCSV(const fs::path& path, std::string type) {

    std::map<std::string, DataRow> data;
    std::ifstream file(path);
    if (!file.is_open()) return data;

    std::string line;
    std::getline(file, line); // skip header

    while (std::getline(file, line)) {

        std::stringstream ss(line);
        std::string token;
        DataRow row;

        std::getline(ss, row.date, ',');

        if (type == "real") {

            if (row.date.rfind("A.D. ", 0) == 0)
                row.date = row.date.substr(5);

            row.date = row.date.substr(0, 11);

            static std::map<std::string, std::string> months = {
                {"Jan","01"},{"Feb","02"},{"Mar","03"},{"Apr","04"},
                {"May","05"},{"Jun","06"},{"Jul","07"},{"Aug","08"},
                {"Sep","09"},{"Oct","10"},{"Nov","11"},{"Dec","12"}
            };

            std::string year = row.date.substr(0, 4);
            std::string mon  = row.date.substr(5, 3);
            std::string day  = row.date.substr(9, 2);

            if (months.count(mon))
                row.date = year + "-" + months[mon] + "-" + day;
        }

        double x, y, z, vx, vy, vz, rmag;

        std::getline(ss, token, ','); x = std::stod(token);
        std::getline(ss, token, ','); y = std::stod(token);
        std::getline(ss, token, ','); z = std::stod(token);
        std::getline(ss, token, ','); vx = std::stod(token);
        std::getline(ss, token, ','); vy = std::stod(token);
        std::getline(ss, token, ','); vz = std::stod(token);
        std::getline(ss, token, ','); rmag = std::stod(token);

        if (type == "manual") {
            row.r_manual = rmag;
            row.v_manual = magnitude(vx, vy, vz);
        }
        if (type == "real") {
            row.r_real = rmag;
            row.v_real = magnitude(vx, vy, vz);
        }

        data[row.date] = row;
    }

    return data;
}

// =====================
// SAMPLE STANDARD DEVIATION
// =====================
static double sampleStd(const std::vector<double>& v, double mean) {

    if (v.size() < 2) return 0.0;

    double sum = 0;
    for (double x : v)
        sum += (x - mean) * (x - mean);

    return std::sqrt(sum / (v.size() - 1));
}

// =====================
// MAIN
// =====================
int main() {

    fs::create_directories(OUTPUT_DIR);

    std::vector<double> all_dr, all_dv;
    std::vector<std::pair<std::string, std::vector<DataRow>>> objects;

    // ================= PASS 1 =================
    for (auto& file : fs::directory_iterator(MANUAL_DIR)) {

        if (file.path().extension() != ".csv")
            continue;

        std::string name = file.path().stem().string();

        // convert underscores to spaces to match real file naming
        std::string realName = name;
        std::replace(realName.begin(), realName.end(), '_', ' ');

        fs::path realPath = fs::path(REAL_DIR) / (realName + "_Real.csv");

        if (!fs::exists(realPath))
            continue;

        auto manual = loadCSV(file.path(), "manual");
        auto real   = loadCSV(realPath, "real");

        std::vector<DataRow> rows;

        for (auto& [date, m] : manual) {

            if (real.count(date)) {

                DataRow r;
                r.date = date;
                r.r_manual = m.r_manual;
                r.v_manual = m.v_manual;
                r.r_real = real[date].r_real;
                r.v_real = real[date].v_real;

                r.delta_r = std::abs(r.r_manual - r.r_real);
                r.delta_v = std::abs(r.v_manual - r.v_real);

                all_dr.push_back(r.delta_r);
                all_dv.push_back(r.delta_v);

                rows.push_back(r);
            }
        }

        if (!rows.empty())
            objects.push_back({ name, rows });
    }

    if (all_dr.empty() || all_dv.empty()) {
        std::cerr << "No overlapping manual/real data found.\n";
        return -1;
    }

    // ================= GLOBAL STATS =================
    double mu_dr = std::accumulate(all_dr.begin(), all_dr.end(), 0.0) / all_dr.size();
    double mu_dv = std::accumulate(all_dv.begin(), all_dv.end(), 0.0) / all_dv.size();

    double std_dr = sampleStd(all_dr, mu_dr);
    double std_dv = sampleStd(all_dv, mu_dv);

    if (std_dr == 0) std_dr = 1e-12;
    if (std_dv == 0) std_dv = 1e-12;

    std::ofstream summary(OUTPUT_DIR + "/ZScore_Summary_XAI.csv");
    summary << "object,max_z_score,anomaly_count,velocity_dominated_anomalies,"
               "position_dominated_anomalies,dominant_error_mode,"
               "temporal_behavior,physical_interpretation,stability_class\n";

    // ================= PASS 2 =================
    for (auto& obj : objects) {

        auto& name = obj.first;
        auto& rows = obj.second;

        int vel_dom = 0, pos_dom = 0, total_anom = 0;
        double max_z = 0;

        std::ofstream out(OUTPUT_DIR + "/" + name + "_ZScore.csv");
        out << "date,delta_r,delta_v,z_r,z_v,z_score,anomaly\n";

        // ---- Compute per-object mean and std ----
        std::vector<double> obj_dr, obj_dv;

        for (auto& r : rows) {
            obj_dr.push_back(r.delta_r);
            obj_dv.push_back(r.delta_v);
        }

        double mu_obj_dr = std::accumulate(obj_dr.begin(), obj_dr.end(), 0.0) / obj_dr.size();
        double mu_obj_dv = std::accumulate(obj_dv.begin(), obj_dv.end(), 0.0) / obj_dv.size();

        double std_obj_dr = sampleStd(obj_dr, mu_obj_dr);
        double std_obj_dv = sampleStd(obj_dv, mu_obj_dv);

        // ---- Compute Z-scores using per-object stats ----
        for (auto& r : rows) {

            if (std_obj_dr > 0)
                r.z_r = std::abs(r.delta_r - mu_obj_dr) / std_obj_dr;
            else
                r.z_r = 0.0;

            if (std_obj_dv > 0)
                r.z_v = std::abs(r.delta_v - mu_obj_dv) / std_obj_dv;
            else
                r.z_v = 0.0;

            r.z_score = std::max(r.z_r, r.z_v);
            r.anomaly = (r.z_score >= Z_THRESHOLD) ? 1 : 0;

            if (r.anomaly) {
                total_anom++;
                if (r.z_v > r.z_r)
                    vel_dom++;
                else
                    pos_dom++;
            }

            if (r.z_score > max_z)
                max_z = r.z_score;

            out << r.date << ","
                << r.delta_r << ","
                << r.delta_v << ","
                << r.z_r << ","
                << r.z_v << ","
                << r.z_score << ","
                << r.anomaly << "\n";
        }
        // -------- Explainability --------
        std::string dominant_mode;
        if (total_anom == 0) dominant_mode = "None";
        else if (pos_dom > vel_dom) dominant_mode = "Position";
        else dominant_mode = "Velocity";

        std::string temporal;
        if (total_anom >= 3) temporal = "Persistent";
        else if (total_anom > 0) temporal = "Isolated";
        else temporal = "None";

        std::string explanation;
        if (dominant_mode == "Position")
            explanation = "Long-term orbital geometry deviation";
        else if (dominant_mode == "Velocity")
            explanation = "Short-term dynamical instability";
        else
            explanation = "Consistent with reference ephemeris";

        std::string stability;
        if (total_anom == 0) stability = "Stable";
        else if (max_z < 4.0) stability = "Marginally Stable";
        else stability = "Unstable";

        summary << name << ","
                << max_z << ","
                << total_anom << ","
                << vel_dom << ","
                << pos_dom << ","
                << dominant_mode << ","
                << temporal << ","
                << explanation << ","
                << stability << "\n";
    }

    summary.close();
    std::cout << "Z-score anomaly analysis complete for "
              << objects.size() << " objects.\n";

    return 0;
}