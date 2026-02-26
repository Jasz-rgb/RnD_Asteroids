#pragma once
#include <string>
#include <vector>

struct DataRow {
    std::string date;

    double r_manual, v_manual;
    double r_real, v_real;

    double delta_r;
    double delta_v;

    double z_r;
    double z_v;
    double z_score;

    int anomaly;
};

struct ObjectSummary {
    std::string name;
    double max_z;
    int anomaly_count;
    int vel_dom;
    int pos_dom;

    std::string dominant_mode;
    std::string temporal_behavior;
    std::string physical_interpretation;
    std::string stability_class;
};