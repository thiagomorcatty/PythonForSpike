import motor_pair
import runloop
from hub import port, motion_sensor

async def turn_precise(target_yaw):
    while True:
        current = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw - current
        while error > 180: error -= 360
        while error < -180: error += 360
        if abs(error) < 0.5: break
        steering = 100 if error > 0 else -100
        motor_pair.move(motor_pair.PAIR_1, steering, velocity=100)
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

async def test_sequence(steps, angle_step):
    print("Iniciando Sequência: {}x {}°".format(steps, angle_step))
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(1000)
    
    for i in range(1, steps + 1):
        target = (i * angle_step) % 360
        if target > 180: target -= 360
        print("Passo {}: Alvo {}°".format(i, target))
        await turn_precise(target)
        await runloop.sleep_ms(200)
    
    final_yaw = motion_sensor.tilt_angles()[0] * -0.1
    print("Yaw Final após ciclo: {}°".format(final_yaw))
    print("Erro acumulado: {}°".format(final_yaw))

async def main():
    motor_pair.pair(motor_pair.PAIR_1, port.A, port.B)
    print("Teste 13: Acúmulo de Erro Angular")
    
    await test_sequence(12, 30) # 12x30 = 360
    await runloop.sleep_ms(2000)
    
    await test_sequence(8, 45) # 8x45 = 360
    await runloop.sleep_ms(2000)
    
    await test_sequence(4, 90) # 4x90 = 360

runloop.run(main())
