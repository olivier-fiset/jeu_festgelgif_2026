#include <Arduino.h>
#include "MCPWM.h"

// put function declarations here:
#define PIN_STOP_CHEVAL_1 2
#define PIN_REVERSE_CHEVAL_1 1
#define PIN_STOP_CHEVAL_2 11
#define PIN_REVERSE_CHEVAL_2 10
#define PIN_STOP_CHEVAL_3 7
#define PIN_REVERSE_CHEVAL_3 6
#define PIN_STOP_CHEVAL_4 5
#define PIN_REVERSE_CHEVAL_4 4

const int NB_CHEVAUX = 4;
const int BUFFER_SIZE = 50;
const uint8_t pinBuffer[NB_CHEVAUX][2] = {{PIN_STOP_CHEVAL_1, PIN_REVERSE_CHEVAL_1}, {PIN_STOP_CHEVAL_2, PIN_REVERSE_CHEVAL_2}, {PIN_STOP_CHEVAL_3, PIN_REVERSE_CHEVAL_3}, {PIN_STOP_CHEVAL_4, PIN_REVERSE_CHEVAL_4}};
uint8_t odds[NB_CHEVAUX] = {2, 3, 5, 10};
uint8_t mises[NB_CHEVAUX];
uint8_t vitesseBuffer[NB_CHEVAUX][BUFFER_SIZE];
MotorDirection directionBuffer[NB_CHEVAUX] = {FORWARD, FORWARD, FORWARD, FORWARD};
bool courseFinieBuffer[NB_CHEVAUX];

#define INTERVALLE_PAR_VITESSE_TICKS pdMS_TO_TICKS(1500)
#define INTERVALLE_IGNORE_SWITCH pdMS_TO_TICKS(1000)
bool courseFinie;
uint8_t nbCoursesFinies;

void remplirBuffers();
void courseFinieCallback(MotorNumber cheval);
void changeDirectionCallback(MotorNumber cheval);
void setNewSpeeds(uint8_t index);

void PollingReverseAndStop(uint8_t currentIndex, MotorNumber cheval);
void ResetCourse();

void secretSauce();

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(0xFFFFFFFF);

  MCPWM_init(MOTOR_1);
  MCPWM_init(MOTOR_2);
  MCPWM_init(MOTOR_3);
  MCPWM_init(MOTOR_4);

  pinMode(PIN_STOP_CHEVAL_1, INPUT);
  pinMode(PIN_REVERSE_CHEVAL_1, INPUT);

  pinMode(PIN_STOP_CHEVAL_2, INPUT);
  pinMode(PIN_REVERSE_CHEVAL_2, INPUT);

  pinMode(PIN_STOP_CHEVAL_3, INPUT);
  pinMode(PIN_REVERSE_CHEVAL_3, INPUT);

  pinMode(PIN_STOP_CHEVAL_4, INPUT);
  pinMode(PIN_REVERSE_CHEVAL_4, INPUT);
}

void loop()
{
  delay(10000);
  Serial.println("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n");
  Serial.println("=== Nouvelle Course ===");
  Serial.println("\n=== ODDS ===");
  Serial.println("Cheval 1 : 2.0");
  Serial.println("Cheval 2 : 3.0");
  Serial.println("Cheval 3 : 5.0");
  Serial.println("Cheval 4 : 10.0");
  Serial.println("\n\n=== ENTREZ LES MISES ===");

  for (int i = 0; i < NB_CHEVAUX; i++)
  {
    Serial.print("Mise cheval ");
    Serial.print(i + 1);
    Serial.print(" : ");

    mises[i] = Serial.parseInt();

    Serial.print(" -> Enregistré: ");
    Serial.println(mises[i]);
  }

  Serial.print("PRESS TO START RACE");
  Serial.parseInt();

  // vrai code
  uint32_t currentTick;
  uint32_t lastSpeedChangeTick = 0;
  uint8_t currentIndex = 0;
  uint32_t raceBeginTick = xTaskGetTickCount();
  ResetCourse();
  // secretSauce();
  remplirBuffers();
  setNewSpeeds(currentIndex);

  while (!courseFinie)
  {
    if (xTaskGetTickCount() - raceBeginTick >= INTERVALLE_IGNORE_SWITCH)
    {
      PollingReverseAndStop(currentIndex, MOTOR_1);
      PollingReverseAndStop(currentIndex, MOTOR_2);
      PollingReverseAndStop(currentIndex, MOTOR_3);
      PollingReverseAndStop(currentIndex, MOTOR_4);
    }
    currentTick = xTaskGetTickCount();
    if (currentTick - lastSpeedChangeTick >= INTERVALLE_PAR_VITESSE_TICKS)
    {
      currentIndex = (currentIndex + 1) % BUFFER_SIZE;
      setNewSpeeds(currentIndex);
      lastSpeedChangeTick = xTaskGetTickCount();
    }
  }

  Serial.print("\nGagnant: ");
}

// put function definitions here:
void ResetCourse()
{
  courseFinie = false;
  nbCoursesFinies = 0;

  for (uint8_t i = 0; i < 4; i++)
  {
    courseFinieBuffer[i] = false;
    directionBuffer[i] = FORWARD;
  }
}

void PollingReverseAndStop(uint8_t currentIndex, MotorNumber cheval)
{
  if (!courseFinieBuffer[cheval])
  {
    if (digitalRead(pinBuffer[cheval][0]) == HIGH)
    {
      if (digitalRead(pinBuffer[cheval][1]) == LOW)
      {
        changeDirectionCallback(cheval);
      }
    }
    else
    {
      courseFinieCallback(cheval);
    }
  }
}

void setNewSpeeds(uint8_t index)
{
  if (!courseFinieBuffer[MOTOR_1])
  {
    MCPWM_setSpeed(MOTOR_1, vitesseBuffer[0][index]);
    MCPWM_setDirection(MOTOR_1, directionBuffer[0]);
  }

  if (!courseFinieBuffer[MOTOR_2])
  {
    MCPWM_setSpeed(MOTOR_2, vitesseBuffer[1][index]);
    MCPWM_setDirection(MOTOR_2, directionBuffer[1]);
  }

  if (!courseFinieBuffer[MOTOR_3])
  {
    MCPWM_setSpeed(MOTOR_3, vitesseBuffer[2][index]);
    MCPWM_setDirection(MOTOR_3, directionBuffer[2]);
  }

  if (!courseFinieBuffer[MOTOR_4])
  {
    MCPWM_setSpeed(MOTOR_4, vitesseBuffer[3][index]);
    MCPWM_setDirection(MOTOR_4, directionBuffer[3]);
  }
}

void changeDirectionCallback(MotorNumber cheval)
{
  directionBuffer[cheval] = REVERSE;
  MCPWM_setDirection(cheval, directionBuffer[cheval]);
}

void courseFinieCallback(MotorNumber cheval)
{
  MCPWM_setSpeed(cheval, 0);
  MCPWM_setDirection(cheval, STOP);

  nbCoursesFinies++;
  if (nbCoursesFinies == 4)
  {
    courseFinie = true;
  }
  courseFinieBuffer[cheval] = true;
}

void secretSauce(){
  for(uint8_t i = 0; i < NB_CHEVAUX; i++){
    if(mises[i] >= 10 && mises[i] < 20){
      odds[i] *= 2;
    }
    else if(mises[i] >= 20){
      odds[i] *= 4;
    }
  }
}

void remplirBuffers()
{
  float performance[NB_CHEVAUX];
  float somme = 0;

  // Calculer la performance normalisée
  for (int i = 0; i < NB_CHEVAUX; i++)
  {
    performance[i] = 1.0 / odds[i]; // inverse des odds
    somme += performance[i];
  }
  for (int i = 0; i < NB_CHEVAUX; i++)
  {
    performance[i] /= somme; // normalisation
  }

  // Remplir les buffers
  for (int i = 0; i < NB_CHEVAUX; i++)
  {
    for (int j = 0; j < BUFFER_SIZE; j++)
    {
      float r = random(0, 1000) / 1000.0; // 0..1 aléatoire
      float biais = pow(r, 1.0 / (performance[i] * 10 + 0.1));
      vitesseBuffer[i][j] = (uint8_t)(biais * 100.0); // convertir en 0..100
    }
  }
}
