
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <Adafruit_NeoPixel.h>
#include <NeoPixelBus.h>

#define LED_NUM 42
#define LED_PIN D2
#define BUFFER_LEN 1024

/* -- Wifi and Socket settings -- */
WiFiUDP port;
IPAddress ip(192, 168, 0, 101);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

const char *ssid = "....";
const char *password = "....";
const uint8_t PixelPin = 3;

unsigned int localPort = 7777;

/* -- NeoPixelBus setup -- */
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_NUM, LED_PIN, NEO_GRB + NEO_KHZ800);


long unsigned int packetSize;
unsigned int len;
int r, g, b;

void setup() {

  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.config(ip, gateway, subnet);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  port.begin(localPort);

  Serial.println("");
  Serial.print("Connected to ");
  Serial.println(ssid);
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Local port: ");
  Serial.println(localPort);
  
  strip.begin();
  strip.show();
}

void loop() {
  int packetSize = port.parsePacket();

  if (packetSize) {
    Serial.println(packetSize);
  }

  if (packetSize) {
    char packetBuffer[packetSize];
    len = port.read(packetBuffer, packetSize);

    if (len > 0) {
      packetBuffer[len] = 0;
    }

    Serial.println(packetBuffer);

    for (int i = 0; i < len; i += 3) {
      // r = (int)(byte *)(packetBuffer)[i];
      // g = (int)(byte *)(packetBuffer)[i + 1];
      // b = (int)(byte *)(packetBuffer)[i + 2];
      RgbColor pixel((uint8_t)packetBuffer[i], (uint8_t)packetBuffer[i+1], (uint8_t)packetBuffer[i+2]);
      
      // strip.setPixelColor(i / 3, r, g, b);
      strip.setPixelColor(i / 3, pixel.G, pixel.B, pixel.R);
    }


    strip.show();
  }

}