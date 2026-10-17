#include <Arduino.h>
#include <Adafruit_BME280.h>
#include <Encoder.h>
#include <Wire.h>
#include <stdlib.h>

// Local variables
namespace {
    unsigned long lastSample    = 0;
    unsigned long INTERVAL      = 100;
    Adafruit_BME280 bme;                                // Create an instance of the BME280 sensor
    Encoder encoder(2, 3);                              // Create an Encoder object with pins 2 and 3
}

// Functions
int readPotentiometer();
int readEncoder(Encoder& encoder);
bool setupBME280();
void readBME280();
void handleSerial();

void setup() {
  Serial.begin(115200);
  Serial.println("Hello, World!");
  Serial.println("Initializing BME280 sensor...");
  while (!setupBME280()) {
    Serial.println("Failed to initialize BME280 sensor.");
    delay(1000);
  }
}

// Target output: {ms, temp, pressure, humidity, pot, enc}
void loop() {
    auto currentMillis = millis();    

    handleSerial();
    if(currentMillis - lastSample >= INTERVAL) {
        Serial.print(currentMillis);
        Serial.print(',');
        Serial.print(bme.readTemperature(), 2);         // 2 decimals
        Serial.print(',');
        Serial.print(bme.readPressure() / 100.0F, 2);   // 2 decimals
        Serial.print(',');
        Serial.print(bme.readHumidity(), 2);            // 2 decimals
        Serial.print(',');
        Serial.print(readPotentiometer());
        Serial.print(',');
        Serial.print(readEncoder(encoder));
        Serial.println();
        lastSample = currentMillis;
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
return bme.begin(0x76);                                 // true if a BME280 answered
}

void handleSerial() {
    static char buf[32];                                // survives between calls
    static uint8_t len = 0;

    while (Serial.available() > 0) {
        char c = Serial.read();

        if (c == '\r') continue;                        // ignore CR from CRLF

        if (c == '\n') {                                // line complete
            if (len == 0) continue;                     // ignore empty lines
            buf[len] = '\0';
            len = 0;

            if (strncmp(buf, "INTERVAL ", 5) == 0) {
                INTERVAL = constrain(atol(buf + 5), 20, 10000);
                Serial.print("# interval set to ");
                Serial.println(INTERVAL);
            } else {
                Serial.println("# unknown command");
            }
        } else if (len < sizeof(buf) - 1) {             // leave room for '\0'
            buf[len++] = c;                             // extra chars are dropped
        }
    }
}