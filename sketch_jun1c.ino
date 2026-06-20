#include <Servo.h>

// Pines
int PIN_TRIG = 9;
int PIN_ECHO  = 10;
int PIN_SERVO = 6;
int PIN_LED = 11;

// Configuracion extra
int BAUDIOS = 9600;
int DELAY_SERVO = 20;     // ms entre cada paso del servo
int PASO_ANGULO = 2;    // grados por movimiento
int MAX_DISTANCIA = 200;    // cm — rango máximo válido del sensor

Servo servo;

int angulo = 0;
int direccion = 1;   // 1 = avanzando hacia 180°, -1 = regresando hacia 0°

unsigned long t_ultimo_led = 0;
bool estado_led = false;

// MEDIR DISTANCIA 
float medirDistancia() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  // Leer cuánto tiempo estuvo HIGH el ECHO
  // Timeout de 30000 evita que pulseIn bloquee si no hay respuesta (aprox 510cm)
  long duracion = pulseIn(PIN_ECHO, HIGH, 30000);

  // Convertir a cm
  float distancia = (duracion * 0.0343) / 2.0;

  return distancia;
}

// SETUP
void setup() {
  Serial.begin(BAUDIOS);

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_LED,  OUTPUT);

  servo.attach(PIN_SERVO);
  servo.write(angulo);
  delay(500); // dejar que el servo llegue a 0° antes de empezar
}

// ============================================================
// LOOP PRINCIPAL
// ============================================================
void loop() {
  // Mover servo y esperar que se estabilice
  servo.write(angulo);
  delay(DELAY_SERVO);

  // Tomar lectura
  float distancia = medirDistancia();

  // Enviar por serial: "angulo,distancia\n"
  // Si la lectura es inválida (0 o fuera de rango), enviar MAX+1 para indicar sin objeto
  if (distancia > 0 && distancia <= MAX_DISTANCIA) {
    Serial.print(angulo);
    Serial.print(",");
    Serial.println(distancia, 1);
  } else {
    Serial.print(angulo);
    Serial.print(",");
    Serial.println(MAX_DISTANCIA + 1);
  }

  // Avanzar ángulo de la pasada
  angulo += direccion * PASO_ANGULO;
  if (angulo >= 180) {
    angulo    = 180;
    direccion = -1;
  } else if (angulo <= 0) {
    angulo    = 0;
    direccion = 1;
  }

  // Parpadeo del LED usando millis() para no bloquear todo
  unsigned long ahora = millis();
  if (ahora - t_ultimo_led >= 500) {
    t_ultimo_led = ahora;
    estado_led   = !estado_led;
    digitalWrite(PIN_LED, estado_led);
  }
}