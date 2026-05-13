import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

async def move_straight_with_gyro(pair, duration_ms, target_yaw, velocity):
    """
    Move o robô em linha reta usando o giroscópio para corrigir o steering em tempo real.
    """
    start_time = utime.ticks_ms()
    # Ganho proporcional (ajuste se a correção for muito lenta ou muito brusca)
    kp = 2.5 
    
    print("Andando reto com correção... Alvo: {:.1f}°".format(target_yaw))
    
    while utime.ticks_diff(utime.ticks_ms(), start_time) < duration_ms:
        current_yaw = motion_sensor.tilt_angles()[0] / 10.0
        
        # Calcula o erro (o quanto estamos fora do caminho)
        error = target_yaw - current_yaw
        
        # Normaliza o erro para o intervalo [-180, 180]
        while error > 180: error -= 360
        while error < -180: error += 360
        
        # Calcula a correção (steering)
        # Se error for positivo (alvo > atual), precisamos virar para a esquerda (steering negativo no SPIKE?)
        # Nota: No SPIKE 3, steering positivo geralmente vira para a direita.
        # Se estamos a 2° e o alvo é 0°, erro é -2. Precisamos virar para a esquerda -> steering negativo.
        correction = error * kp
        
        # Limita o steering para não ser muito brusco (ex: max 30)
        if correction > 30: correction = 30
        if correction < -30: correction = -30
        
        # Aplica o movimento com a correção
        motor_pair.move(pair, int(correction), velocity=velocity)
        
        await runloop.sleep_ms(10)
    
    motor_pair.stop(pair)

async def turn_to_angle(pair, target_yaw_deg, velocity):
    """
    Gira o robô até um ângulo absoluto com precisão.
    """
    steering_speed = 100
    
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] / 10.0
        error = target_yaw_deg - current_yaw
        
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 0.5: # Margem de erro bem pequena
            break
            
        # Direção da curva
        steering = 100 if error > 0 else -100
        
        # Reduz a velocidade quando estiver chegando perto para não passar do ponto
        current_vel = velocity if abs(error) > 20 else int(velocity * 0.5)
        if current_vel < 50: current_vel = 50
        
        motor_pair.move(pair, steering, velocity=current_vel)
        await runloop.sleep_ms(10)
        
    motor_pair.stop(pair)

async def main():
    print("--- Teste 4: Quadrado com Correção de Giroscópio ---")
    
    p_left = port.A
    p_right = port.B
    
    # Alinhamento e calibração
    print("Preparando...")
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(2000) # Tempo extra para o giroscópio estabilizar
    
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    velocidade_reta = 400
    velocidade_giro = 150 # Giro mais lento = mais precisão
    tempo_lado_ms = 2000
    
    for i in range(4):
        lado = i + 1
        # O alvo de cada lado é o ângulo que acabamos de virar
        alvo_yaw = (i * 90) % 360
        if alvo_yaw > 180: alvo_yaw -= 360
        
        print("\n--- Lado {} | Alvo de Direção: {}° ---".format(lado, alvo_yaw))
        
        # 1. Movimento em linha reta com CORREÇÃO ATIVA
        await move_straight_with_gyro(motor_pair.PAIR_1, tempo_lado_ms, alvo_yaw, velocidade_reta)
        
        await runloop.sleep_ms(400)
        
        # 2. Curva para o próximo ângulo
        proximo_alvo = ((i + 1) * 90) % 360
        if proximo_alvo > 180: proximo_alvo -= 360
        
        await turn_to_angle(motor_pair.PAIR_1, proximo_alvo, velocidade_giro)
        await runloop.sleep_ms(400)

    print("\nQuadrado Corrigido Concluído!")
    print("Erro final de orientação: {:.2f}°".format(motion_sensor.tilt_angles()[0] / 10.0))

runloop.run(main())
