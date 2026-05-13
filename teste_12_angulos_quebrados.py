import motor_pair
import runloop
from hub import port, motion_sensor

async def turn_precise(target_yaw, velocity=150):
    while True:
        current = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw - current
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 0.5: break
            
        steering = 100 if error > 0 else -100
        curr_v = velocity if abs(error) > 10 else 50
        motor_pair.move(motor_pair.PAIR_1, steering, velocity=curr_v)
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    print("Teste 12: Ângulos Quebrados")
    
    # Sequência de ângulos solicitada
    angulos = [15, 30, 45, 60, 75, 120, 135, 150]
    
    for a in angulos:
        print("Girando para {}°".format(a))
        await turn_precise(a)
        await runloop.sleep_ms(1000)
    
    print("Retornando para 0°")
    await turn_precise(0)
    
    print("Teste de simetria (45° Dir -> 45° Esq)")
    await turn_precise(45)
    await runloop.sleep_ms(1000)
    await turn_precise(0)
    print("Simetria finalizada.")

runloop.run(main())
