#include <iostream>
#include <string>
#include <fstream>
#include <dirent.h>
#include <unistd.h>
#include <vector>

int getGpuTemp() {
    std::ifstream tempFile("/sys/class/hwmon/hwmon4/temp1_input");
    if (tempFile.is_open()) {
        int temp;
        tempFile >> temp;
        return temp / 1000;
    }
    return 0;
}

class Process {
    private:
        int temp_system;
        long ram_mb;
        int pid;
        std::string name;

    public:
        Process(int p, int temp) : pid(p), temp_system(temp), ram_mb(0) {
            update();
        }

        void update() {
            std::ifstream nameFile("/proc/" + std::to_string(pid) + "/comm");
            if (nameFile.is_open()) std::getline(nameFile, name);
            else name = "unknown";

            std::ifstream memFile("/proc/" + std::to_string(pid) + "/statm");
            long total, rss;
            if (memFile >> total >> rss) {
                ram_mb = (rss * sysconf(_SC_PAGESIZE)) / 1024 / 1024;
            } else {
                ram_mb = 0;
            }
        }

        void getInfo() {
            if (ram_mb > 0) {
                std::cout << "Name: " << name 
                          << " | RAM: " << ram_mb << " MB"
                          << " | PID: " << pid 
                          << " | SysTemp: " << temp_system << "C" << std::endl;
            }
        }
};

int main() {
    while (true) {
        int current_temp = getGpuTemp();
        std::cout << "\033[2J\033[1;1H";
        std::cout << "--- System Monitor ---" << std::endl;
        
        DIR* dir = opendir("/proc");
        if (dir) {
            struct dirent* entry;
            while ((entry = readdir(dir)) != nullptr) {
                if (isdigit(entry->d_name[0])) {
                    Process p(std::stoi(entry->d_name), current_temp);
                    p.getInfo();
                }
            }
            closedir(dir);
        }
        
        sleep(10);
    }
    return 0;
}