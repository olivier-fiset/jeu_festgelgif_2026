#include <Arduino.h>
#include "MCPWM.h"

// put function declarations here:

const int NB_CHEVAUX = 4;
const int BUFFER_SIZE = 50;
const uint8_t odds[NB_CHEVAUX] = {2, 3, 5, 10};
uint8_t mises[NB_CHEVAUX];
uint8_t vitesseBuffer[NB_CHEVAUX][BUFFER_SIZE];
MotorDirection directionBuffer[NB_CHEVAUX];
bool courseFinieBuffer[NB_CHEVAUX];
MotorNumber gagnant;

#define INTERVALLE_PAR_VITESSE_TICKS pdMS_TO_TICKS(500)
bool courseFinie = false;

void remplirBuffers();
void courseFinieCallback();
void setNewSpeeds(uint8_t index);

void setup()
{
  // put your setup code here, to run once:
  Serial.begin(115200);

  MCPWM_init(MOTOR_1);
  MCPWM_init(MOTOR_2);
  MCPWM_init(MOTOR_3);
  MCPWM_init(MOTOR_4);

  pinMode(1, INPUT);
  pinMode(2, INPUT);
  pinMode(4, OUTPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);
  pinMode(10, INPUT);
  pinMode(11, INPUT);
}

void loop()
{
  // Serial.println("\n=== ENTREZ LES MISES ===");
  // for (int i = 0; i < NB_CHEVAUX; i++)
  // {
  //   Serial.println("\n Mise Cheval ");
  //   Serial.println(i);
  //   Serial.println(": ");
  //   mises[i] = Serial.parseInt();
  // }

  // // test code:
  // MCPWM_setSpeed(MOTOR_1, 100);
  // MCPWM_setDirection(MOTOR_1, FORWARD);
  // delay(3000);

  // if (IO_read(MCP23017_GPIOA_REG, IOA, PIN0))
  // {
  //   MCPWM_setSpeed(MOTOR_1, 0);
  //   MCPWM_setDirection(MOTOR_1, STOP);
  //   delay(10000);
  // }
  //////

  // vrai code
  // uint32_t currentTick;
  // uint32_t lastSpeedChangeTick = 0;
  // uint8_t currentIndex = 0;
  // remplirBuffers();
  // setNewSpeeds(currentIndex);

  if (digitalRead(2))
  {
    digitalWrite(4, HIGH);
  }
  else
  {
    digitalWrite(4, LOW);
  }
  // while(!courseFinie){
  //   currentTick = xTaskGetTickCount();
  //   if(currentTick - lastSpeedChangeTick >= INTERVALLE_PAR_VITESSE_TICKS){
  //     currentIndex++;
  //   }
  // }
  // while(courseFinie){
  //   // read IO for button to start new race
  // }
}

// put function definitions here:

void setNewSpeeds(uint8_t index)
{
  MCPWM_setSpeed(MOTOR_1, vitesseBuffer[0][index]);
  MCPWM_setDirection(MOTOR_1, directionBuffer[0]);

  MCPWM_setSpeed(MOTOR_2, vitesseBuffer[1][index]);
  MCPWM_setDirection(MOTOR_2, directionBuffer[1]);

  MCPWM_setSpeed(MOTOR_3, vitesseBuffer[2][index]);
  MCPWM_setDirection(MOTOR_3, directionBuffer[2]);

  MCPWM_setSpeed(MOTOR_4, vitesseBuffer[3][index]);
  MCPWM_setDirection(MOTOR_4, directionBuffer[3]);
}

void changeDirectionCallback(MotorNumber cheval)
{
  directionBuffer[cheval] = REVERSE;
}

void courseFinieCallback(MotorNumber cheval)
{
  // if(gagnant == 0){
  //   gagnant = cheval;
  // }
  courseFinieBuffer[cheval] = true;

  MCPWM_setSpeed(cheval, 0);
  MCPWM_setDirection(cheval, STOP);
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