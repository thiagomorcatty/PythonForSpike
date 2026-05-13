import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

async def turn_to_angle(pair, target_yaw_deg, velocity):
    """
    Gira o robô até atingir um ângulo absoluto específico usando o giroscópio.
    """
    # Determina a direção (curto caminho)
    current_yaw = motion_sensor.tilt_angles()[0] / 10.0
    diff = target_yaw_deg - current_yaw
    
    # Normaliza a diferença para o intervalo [-180, 180]
    while diff > 180: diff -= 360
    while diff < -180: diff += 360
    
    steering = 100 if diff > 0 else -100
    
    print("Girando para o ângulo {:.1f}°...".format(target_yaw_deg))
    
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] / 10.0
        remaining = target_yaw_deg - current_yaw
        
        # Se estiver muito perto do alvo (ex: 1 grau), para
        if abs(remaining) < 1.0:
            break
            
        motor_pair.move(pair, steering, velocity=velocity)
        await runloop.sleep_ms(10)
    
    motor_pair.stop(pair)
    print("Ângulo atingido: {:.1f}°".format(motion_sensor.tilt_angles()[0] / 10.0))

async def main():
    print("--- Teste 3: Quadrado Perfeito com Giroscópio ---")
    
    p_left = port.A
    p_right = port.B
    
    # Alinhamento e calibração
    print("Alinhando e aguardando estabilização...")
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(1000)
    
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    velocidade_reta = 400
    velocidade_giro = 200
    tempo_lado_ms = 2000 # 2 segundos
    
    # Loop para os 4 lados do quadrado
    for i in range(4):
        lado = i + 1
        print("\n--- Lado {} ---".format(lado))
        
        # 1. Movimento em linha reta por 2 segundos
        # Usamos steering=0 para ir reto
        await motor_pair.move_for_time(motor_pair.PAIR_1, tempo_lado_ms, 0, velocity=velocidade_reta)
        
        # Pequena pausa para estabilizar antes da curva
        await runloop.sleep_ms(500)
        
        # 2. Curva de 90 graus
        # O alvo será 90, 180, 270 (ou -90), 0
        alvo_yaw = (lado * 90) % 360
        # O SPIKE costuma usar range -180 a 180, então vamos ajustar
        if alvo_yaw > 180: alvo_yaw -= 360
        
        print("Curva para {}°...".format(alvo_yaw))
        await turn_to_angle(motor_pair.PAIR_1, alvo_yaw, velocidade_giro)
        
        await runloop.sleep_ms(500)

    print("\nQuadrado concluído! O robô deve estar na posição inicial.")

runloop.run(main())
