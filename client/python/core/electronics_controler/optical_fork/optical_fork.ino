const int capteurPin = 3; // Broche numérique où le capteur est connecté

void setup() {
  Serial.begin(9600); // Initialise la communication série à 9600 bauds
  pinMode(capteurPin, INPUT); // Configure la broche du capteur en entrée
}

void loop() {
  int etatCapteur = digitalRead(capteurPin); // Lis l'état du capteur (LOW ou HIGH)
  
  if (etatCapteur == LOW) {
    Serial.println("Fourche optique libre"); // Affiche le message si le capteur est obstrué
  } else {
    Serial.println("Fourche optique obstruée"); // Affiche le message si le capteur est libre
  }


}
