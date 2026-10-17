#include <Arduino.h>
#include <Adafruit_BME280.h>
#include <Encoder.h>
#include <Wire.h>

// Local variables
namespace {
    unsigned long lastSample    = 0;
    unsigned long INTERVAL      = 50;
    Adafruit_BME280 bme;                // Create an instance of the BME280 sensor
    Encoder encoder(2, 3);              // Create an Encoder object with pins 2 and 3
}

// Functions
int readPotentiometer();
int readEncoder(Encoder& encoder);
bool setupBME280();
void readBME280();

void setup() {
  Serial.begin(115200);
  Serial.println("Hello, World!");
  while (!setupBME280()) {
    Serial.println("Failed to initialize BME280 sensor.");
    }
}

void loop() {
    auto currentMillis = millis();
    if(currentMillis - lastSample >= INTERVAL) {
        Serial.print("Current millis: ");
        Serial.println(currentMillis);
        lastSample = currentMillis;

        Serial.print("Potentiometer value: ");
        int potValue = readPotentiometer();
        Serial.println(potValue);

        Serial.print("Encoder value: ");
        int encValue = readEncoder(encoder);
        Serial.println(encValue);

        readBME280();
    }
}

int readPotentiometer() {
    int potValue = analogRead(A0);
    return potValue;
}

int readEncoder(Encoder& encoder) {
    int encValue = encoder.read();
    return encValue;
}

bool setupBME280() {
return bme.begin(0x76);             // true if a BME280 answered
}

void readBME280() {
    float temperature = bme.readTemperature();        // degrees C
    float pressure    = bme.readPressure() / 100.0F;  // Pa to hPa
    float humidity    = bme.readHumidity();           // percent

    Serial.print("Temperature: ");
    Serial.println(temperature, 2);
    Serial.print("Pressure: ");
    Serial.println(pressure, 2);
    Serial.print("Humidity: ");
    Serial.println(humidity, 2);
}