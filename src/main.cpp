#include <Arduino.h>
#include "MCPWM.h"

// put function declarations here:
#define CHEVAL_1 0
#define CHEVAL_2 1
#define CHEVAL_3 2
#define CHEVAL_4 3

#define INTERVALLE_PAR_VITESSE_TICKS pdMS_TO_TICKS(500)
bool courseFinie = false;
uint8_t bufferVitesse1[10] = {0};
uint8_t bufferVitesse2[10] = {0};
uint8_t bufferVitesse3[10] = {0};
uint8_t bufferVitesse4[10] = {0};
void remplirBufferVitesses(void);

void setup()
{
  // put your setup code here, to run once:
  MCPWM_init(MOTOR_1);
  MCPWM_init(MOTOR_2);
  MCPWM_init(MOTOR_3);
  MCPWM_init(MOTOR_4);
}

void loop()
{
  // test code:
  // MCPWM_setSpeed(MOTOR_1, 50);
  // MCPWM_setDirection(MOTOR_1, FORWARD);
  // delay(3000);

  // MCPWM_setSpeed(MOTOR_1, 0);
  // MCPWM_setDirection(MOTOR_1, STOP);
  // delay(3000);
  ////////

  // vrai code
  uint32_t currentTick;
  uint32_t lastSpeedChangeTick = 0;
  uint8_t currentIndex = 0;

  while(!courseFinie){
    currentTick = xTaskGetTickCount();
    if(currentTick - lastSpeedChangeTick >= INTERVALLE_PAR_VITESSE_TICKS){
      currentIndex++;
    }
    // courseFinie = IO_read();
  }



}

// put function definitions here:
void remplirBufferVitesses(void)
{

  for(uint8_t i = 0; i < 10; i++){
    bufferVitesse1[i];
    bufferVitesse2[i];
    bufferVitesse3[i];
    bufferVitesse4[i];
  }
}