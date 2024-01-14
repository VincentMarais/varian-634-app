const int capteurPin = 2 ; // Broche numérique où le capteur est connecté

void setup() {
  Serial.begin(115200); // Initialise la communication série à 9600 bauds
  pinMode(capteurPin, INPUT); // Configure la broche du capteur en entrée
}

void loop() {
  int etatCapteur = digitalRead(capteurPin); // Lis l'état du capteur (LOW ou HIGH)
  
  if (etatCapteur == LOW) {
    Serial.println("up"); // Affiche le message si la Fourche optique libre"
  } else {
    Serial.println("low"); // Affiche le message si la Fourche optique obstruée
  }


}
