//#include <iostream>
//#include <fstream>
//#include <string>
//#include <vector>
//#include <filesystem>
//#include <nlohmann/json.hpp>
//
//using json = nlohmann::json;
//namespace fs = std::filesystem;
//
//const std::string DATA_DIR = "data";
//
//struct OrbitalElements {
//   float a, e, i, Omega, omega, M0;
//};
//
//// Function to read a single JSON file and extract orbital elements
//bool readOrbitalElementsFromJSON(const fs::path& path, OrbitalElements& oe) {
//   std::ifstream ifs(path);
//   if (!ifs.is_open()) return false;
//
//   json j; ifs >> j;
//   std::map<std::string, float> mapv;
//   if (j.contains("orbit") && j["orbit"].contains("elements")) {
//       for (auto& el : j["orbit"]["elements"]) {
//           if (!el.contains("name") || !el.contains("value")) continue;
//           std::string name = el["name"];
//           float v = el["value"].is_string()
//               ? std::stof(el["value"].get<std::string>())
//               : static_cast<float>(el["value"].get<double>());
//           mapv[name] = v;
//       }
//   }
//
//   oe.a = mapv["a"];
//   oe.e = mapv["e"];
//   oe.i = mapv["i"];
//   oe.Omega = mapv["om"];
//   oe.omega = mapv["w"];
//   oe.M0 = mapv["ma"];
//   return true;
//}
//
//int main() {
//   // Read asteroid names from targets.txt
//   std::vector<std::string> targetAsteroids;
//   std::ifstream targetFile("C:/Users/JASMINE/Desktop/RnD_asteroid/targets.txt");
//   if (!targetFile.is_open()) {
//       std::cerr << "Error: Could not open targets.txt\n";
//       return -1;
//   }
//
//   std::string asteroidName;
//   while (std::getline(targetFile, asteroidName)) {
//       if (!asteroidName.empty()) {
//           for (auto& c : asteroidName)
//               if (c == ' ') c = '_';
//           targetAsteroids.push_back(asteroidName + ".json");
//       }
//   }
//   targetFile.close();
//
//   std::cout << "Found " << targetAsteroids.size() << " asteroid names in targets.txt\n";
//
//   // Try loading each file
//   std::vector<OrbitalElements> elements;
//   for (auto& name : targetAsteroids) {
//       fs::path path = fs::path(DATA_DIR) / name;
//       OrbitalElements oe{};
//       if (readOrbitalElementsFromJSON(path, oe)) {
//           elements.push_back(oe);
//           std::cout << "Loaded " << name << "\n";
//       }
//       else {
//           std::cout << "Failed to load " << name << "\n";
//       }
//   }
//
//   std::cout << "\nLoaded " << elements.size() << " asteroid files successfully out of "
//       << targetAsteroids.size() << ".\n";
//
//   return 0;
//}
