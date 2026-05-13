import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

async def move_straight_with_gyro(pair, duration_ms, target_yaw, velocity):
    """
    Move o robô em linha reta usando o giroscópio para corrigir o rumo.
    Funciona para frente (vel > 0) e para trás (vel < 0).
    """
    start_time = utime.ticks_ms()
    kp = 1.2 
    
    print("Iniciando Movimento... Alvo: {:.1f}° | Vel: {}".format(target_yaw, velocity))
    
    while utime.ticks_diff(utime.ticks_ms(), start_time) < duration_ms:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        correction = error * kp
        
        # Inverte a correção se estiver indo de ré para manter a lógica de direção
        # Se estou indo para trás e quero corrigir para a esquerda, o steering deve ser ajustado
        # Na verdade, o motor_pair.move com steering e velocidade negativa inverte o sentido do giro.
        # Vamos testar: se steering=10 (direita) e vel=100 -> gira para direita.
        # Se steering=10 (direita) e vel=-100 -> gira para a direita indo de ré (cauda vai para a esquerda).
        # Para o giroscópio, o que importa é a rotação do hub.
        if velocity < 0:
            correction = -correction

        if correction > 25: correction = 25
        if correction < -25: correction = -25
        
        motor_pair.move(pair, int(correction), velocity=velocity)
        await runloop.sleep_ms(10)
    
    motor_pair.stop(pair)

async def turn_to_angle(pair, target_yaw_deg, velocity):
    """
    Gira o robô até um ângulo absoluto.
    """
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw_deg - current_yaw
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 1.0:
            break
            
        steering = 100 if error > 0 else -100
        current_vel = velocity if abs(error) > 15 else 60
        
        motor_pair.move(pair, steering, velocity=current_vel)
        await runloop.sleep_ms(10)
        
    motor_pair.stop(pair)

async def main():
    print("--- Teste 5: Trajeto com Retorno Preciso ---")
    
    p_left = port.A
    p_right = port.B
    
    # Setup
    print("Alinhando e Calibrando...")
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(2000)
    
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    vel_reta = 350
    vel_giro = 150
    
    # 1. IDA
    print("\n--- FASE 1: IDA ---")
    # Anda 3 segundos reto (0°)
    await move_straight_with_gyro(motor_pair.PAIR_1, 3000, 0, vel_reta)
    await runloop.sleep_ms(500)
    
    # Curva de 60 graus para a direita
    await turn_to_angle(motor_pair.PAIR_1, 60, vel_giro)
    await runloop.sleep_ms(500)
    
    # Anda 2 segundos reto (60°)
    await move_straight_with_gyro(motor_pair.PAIR_1, 2000, 60, vel_reta)
    
    print("Pausa no destino...")
    await runloop.sleep_ms(2000)
    
    # 2. VOLTA (Invertendo o caminho)
    print("\n--- FASE 2: VOLTA ---")
    # Volta 2 segundos de ré (mantendo o ângulo de 60°)
    await move_straight_with_gyro(motor_pair.PAIR_1, 2000, 60, -vel_reta)
    await runloop.sleep_ms(500)
    
    # Gira de volta para 0°
    await turn_to_angle(motor_pair.PAIR_1, 0, vel_giro)
    await runloop.sleep_ms(500)
    
    # Volta 3 segundos de ré (mantendo o ângulo de 0°)
    await move_straight_with_gyro(motor_pair.PAIR_1, 3000, 0, -vel_reta)

    print("\nRetorno concluído!")
    print("Erro de orientação final: {:.2f}°".format(motion_sensor.tilt_angles()[0] * -0.1))

runloop.run(main())
