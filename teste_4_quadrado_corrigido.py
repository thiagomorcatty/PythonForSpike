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
    # Ganho proporcional (ajustado para ser mais suave e evitar a "dança")
    kp = 1.2 
    
    print("Andando reto com correção... Alvo: {:.1f}°".format(target_yaw))
    
    while utime.ticks_diff(utime.ticks_ms(), start_time) < duration_ms:
        # Multiplicamos por -0.1 para que: Direita = Positivo, Esquerda = Negativo
        # Isso alinha o sensor com a convenção do motor_pair.move
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        
        # Calcula o erro
        error = target_yaw - current_yaw
        
        # Normaliza o erro para o intervalo [-180, 180]
        while error > 180: error -= 360
        while error < -180: error += 360
        
        # Agora o sinal deve estar correto: 
        # Se entortar para a direita (yaw positivo), erro será negativo, 
        # resultando em steering negativo (virar para a esquerda).
        correction = error * kp
        
        # Limita o steering para não ser muito brusco
        if correction > 25: correction = 25
        if correction < -25: correction = -25
        
        motor_pair.move(pair, int(correction), velocity=velocity)
        
        await runloop.sleep_ms(10)
    
    motor_pair.stop(pair)

async def turn_to_angle(pair, target_yaw_deg, velocity):
    """
    Gira o robô até um ângulo absoluto com precisão.
    """
    while True:
        current_yaw = motion_sensor.tilt_angles()[0] * -0.1
        error = target_yaw_deg - current_yaw
        
        while error > 180: error -= 360
        while error < -180: error += 360
        
        if abs(error) < 1.0: # Margem de erro
            break
            
        # Direção da curva (steering positivo = Direita)
        # Se erro > 0 (alvo > atual), precisamos virar para a direita
        steering = 100 if error > 0 else -100
        
        # Velocidade adaptativa
        current_vel = velocity if abs(error) > 15 else 60
        
        motor_pair.move(pair, steering, velocity=current_vel)
        await runloop.sleep_ms(10)
        
    motor_pair.stop(pair)

async def main():
    print("--- Teste 4 Corrigido: Quadrado de Precisão ---")
    
    p_left = port.A
    p_right = port.B
    
    # Alinhamento e calibração
    print("Calibrando Giroscópio...")
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    motion_sensor.reset_yaw(0)
    await runloop.sleep_ms(2000)
    
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    velocidade_reta = 350 # Reduzimos um pouco a velocidade para melhorar a correção
    velocidade_giro = 150 
    tempo_lado_ms = 2000
    
    for i in range(4):
        lado = i + 1
        alvo_yaw = (i * 90) % 360
        if alvo_yaw > 180: alvo_yaw -= 360
        
        print("\n--- Lado {} | Rumo: {}° ---".format(lado, alvo_yaw))
        
        # 1. Movimento Reto com Correção
        await move_straight_with_gyro(motor_pair.PAIR_1, tempo_lado_ms, alvo_yaw, velocidade_reta)
        await runloop.sleep_ms(300)
        
        # 2. Curva
        proximo_alvo = ((i + 1) * 90) % 360
        if proximo_alvo > 180: proximo_alvo -= 360
        
        await turn_to_angle(motor_pair.PAIR_1, proximo_alvo, velocidade_giro)
        await runloop.sleep_ms(300)

    print("\nQuadrado Concluído!")
    print("Erro final de orientação: {:.2f}°".format(motion_sensor.tilt_angles()[0] * -0.1))

runloop.run(main())
