#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

#define WIFI_SSID "YOUR_WIFI_SSID"
#define WIFI_PASSWORD "YOUR_WIFI_PASSWORD"

// PI Address configuration. Change to the Raspberry Pi IP
#define PI_SERVER_URL "http://192.168.1.100:5000/sensor_data"

#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// 5 minutes in milliseconds
const long interval = 300000;
unsigned long previousMillis = 0;

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
}

void loop() {
  unsigned long currentMillis = millis();

  // Reconnect WiFi if dropped
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Reconnecting WiFi...");
    WiFi.disconnect();
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
    }
  }

  if (currentMillis - previousMillis >= interval || previousMillis == 0) {
    previousMillis = currentMillis;

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    if (isnan(h) || isnan(t)) {
      Serial.println("Failed to read from DHT sensor!");
      return;
    }

    Serial.print("Temp: ");
    Serial.print(t);
    Serial.print("C, Hum: ");
    Serial.print(h);
    Serial.println("%");

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(PI_SERVER_URL);
      http.addHeader("Content-Type", "application/json");

      String jsonPayload = "{\"sensor_id\":\"esp32_1\",\"temp\":";
      jsonPayload += String(t);
      jsonPayload += ",\"humidity\":";
      jsonPayload += String(h);
      jsonPayload += "}";

      int httpResponseCode = http.POST(jsonPayload);
      if (httpResponseCode > 0) {
        Serial.print("HTTP POST Response: ");
        Serial.println(httpResponseCode);
      } else {
        Serial.print("Error code: ");
        Serial.println(httpResponseCode);
      }
      http.end();
    }
  }
}
