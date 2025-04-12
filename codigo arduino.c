const int trigPin = 3;
const int echoPin = 2;
long duracao;
int distancia;

void setup() {
  Serial.begin(9600);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
}

void loop() {
  // Garante que o Trig está baixo
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Envia pulso de 10 microssegundos
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Lê o tempo de resposta do Echo
  duracao = pulseIn(echoPin, HIGH);

  // Calcula a distância em cm
  distancia = duracao * 0.034 / 2;

  // Imprime no formato solicitado
  Serial.print("Distancia ");
  Serial.println(distancia);
 
  delay(500); // Aguarda meio segundo entre medições
}