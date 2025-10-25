#include <stdio.h>

#define NUM_SAMPLES 50
#define TEMP_THRESHOLD 25.0
#define HUMIDITY_THRESHOLD 60.0

typedef struct {
    float temperature;
    float humidity;
    float pressure;
    int timestamp;
} SensorReading;

SensorReading read_sensor(int iteration) {
    SensorReading reading;
    reading.temperature = 20.0 + (iteration % 15) * 0.5;
    reading.humidity = 50.0 + (iteration % 20) * 1.0;
    reading.pressure = 1013.25 + (iteration % 10) * 0.7;
    reading.timestamp = iteration;
    return reading;
}

void process_data(SensorReading *readings, int count) {
    float temp_sum = 0.0, humidity_sum = 0.0, pressure_sum = 0.0;

    for (int i = 0; i < count; i++) {
        temp_sum += readings[i].temperature;
        humidity_sum += readings[i].humidity;
        pressure_sum += readings[i].pressure;
    }

    printf("\nData Processing Results:\n");
    printf("------------------------\n");
    printf("Average Temperature: %.2f°C\n", temp_sum / count);
    printf("Average Humidity:    %.2f%%\n", humidity_sum / count);
    printf("Average Pressure:    %.2f hPa\n", pressure_sum / count);
}

int check_alerts(SensorReading reading) {
    int alert_count = 0;

    if (reading.temperature > TEMP_THRESHOLD) {
        printf("  [ALERT] High temperature: %.2f°C\n", reading.temperature);
        alert_count++;
    }

    if (reading.humidity > HUMIDITY_THRESHOLD) {
        printf("  [ALERT] High humidity: %.2f%%\n", reading.humidity);
        alert_count++;
    }

    return alert_count;
}

int main() {
    printf("===============================================\n");
    printf("IoT Environmental Sensor Node Simulation\n");
    printf("===============================================\n\n");

    printf("Configuration:\n");
    printf("--------------\n");
    printf("Sample Count:        %d\n", NUM_SAMPLES);
    printf("Temp Threshold:      %.1f°C\n", TEMP_THRESHOLD);
    printf("Humidity Threshold:  %.1f%%\n\n", HUMIDITY_THRESHOLD);

    SensorReading readings[NUM_SAMPLES];
    int total_alerts = 0;

    printf("Starting sensor monitoring cycle...\n");
    printf("===================================\n\n");

    for (int i = 0; i < NUM_SAMPLES; i++) {
        readings[i] = read_sensor(i);

        if (i % 10 == 0) {
            printf("Sample %d:\n", i);
            printf("  Temperature: %.2f°C\n", readings[i].temperature);
            printf("  Humidity:    %.2f%%\n", readings[i].humidity);
            printf("  Pressure:    %.2f hPa\n", readings[i].pressure);

            int alerts = check_alerts(readings[i]);
            total_alerts += alerts;

            printf("\n");
        }
    }

    process_data(readings, NUM_SAMPLES);

    printf("\n===============================================\n");
    printf("Monitoring Summary\n");
    printf("===============================================\n");
    printf("Total Samples:       %d\n", NUM_SAMPLES);
    printf("Total Alerts:        %d\n", total_alerts);
    printf("Alert Rate:          %.1f%%\n", (float)total_alerts/NUM_SAMPLES*100);
    printf("===============================================\n");
    printf("Sensor monitoring completed successfully!\n");
    printf("===============================================\n");

    return 0;
}