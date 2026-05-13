import motor_pair
import runloop
from hub import port, motion_sensor
import utime
import motor

async def test_rotation_with_gyro(pair, left_port, right_port, target_yaw_deg, velocity):
    """
    Realiza uma curva e compara o que os motores acham que giraram 
    com o que o giroscópio mediu.
    """
    print("\n--- Iniciando Teste de Rotação ---")
    
    # 1. Resetar sensores
    motor.reset_relative_position(left_port, 0)
    motor.reset_relative_position(right_port, 0)
    motion_sensor.reset_yaw(0)
    
    await runloop.sleep_ms(500) # Estabilização
    
    start_time = utime.ticks_ms()
    last_print = 0
    
    # Inicia a rotação (steering=100 para girar sobre o próprio eixo)
    # No SPIKE 3, motor_pair.move(pair, steering, velocity)
    # steering=100 gira para a direita, -100 para a esquerda
    steering = 100 if target_yaw_deg > 0 else -100
    
    print("Girando até {} graus de Yaw...".format(target_yaw_deg))
    
    while True:
        # Lê o Giroscópio (index 0 é Yaw, retornado em décimos de grau)
        current_yaw = motion_sensor.tilt_angles()[0] / 10.0
        
        # Lê os Motores
        pos_left = motor.relative_position(left_port)
        pos_right = motor.relative_position(right_port)
        
        # Se atingir o ângulo do giro, para
        if abs(current_yaw) >= abs(target_yaw_deg):
            break
            
        motor_pair.move(pair, steering, velocity=velocity)
        
        # Monitoramento em tempo real
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_print) > 200:
            # Cálculo teórico simples: diferença dos motores
            # Isso é apenas informativo para o usuário comparar
            print("Giro: {:.1f}° | Motores L: {} R: {} | Diff: {}".format(
                current_yaw, pos_left, pos_right, pos_left - pos_right
            ))
            last_print = current_time
            
        await runloop.sleep_ms(10)

    motor_pair.stop(pair)
    
    final_yaw = motion_sensor.tilt_angles()[0] / 10.0
    final_l = motor.relative_position(left_port)
    final_r = motor.relative_position(right_port)
    
    print("--- Resultado da Curva ---")
    print("Yaw Final Giroscópio: {:.1f}°".format(final_yaw))
    print("Motores - Esq: {}°, Dir: {}°".format(final_l, final_r))
    print("Relação (Motores/Giro): {:.2f} graus de motor por grau de giro".format(
        abs(final_l - final_r) / abs(final_yaw) if final_yaw != 0 else 0
    ))

async def test_straight_drift(pair, left_port, right_port, duration_ms, velocity):
    """
    Anda em linha reta e monitora se o giroscópio detecta desvios (drift).
    """
    print("\n--- Iniciando Teste de Linha Reta com Giro ---")
    
    motor.reset_relative_position(left_port, 0)
    motor.reset_relative_position(right_port, 0)
    motion_sensor.reset_yaw(0)
    
    await runloop.sleep_ms(500)
    
    start_time = utime.ticks_ms()
    last_print = 0
    
    print("Andando reto por {}ms...".format(duration_ms))
    
    while utime.ticks_diff(utime.ticks_ms(), start_time) < duration_ms:
        current_yaw = motion_sensor.tilt_angles()[0] / 10.0
        pos_left = motor.relative_position(left_port)
        pos_right = motor.relative_position(right_port)
        
        # Tenta andar reto (steering=0)
        motor_pair.move(pair, 0, velocity=velocity)
        
        current_time = utime.ticks_ms()
        if utime.ticks_diff(current_time, last_print) > 500:
            print("Time: {}ms | Yaw: {:.1f}° | Erro Motores: {}".format(
                utime.ticks_diff(current_time, start_time), current_yaw, pos_left - pos_right
            ))
            last_print = current_time
            
        await runloop.sleep_ms(20)

    motor_pair.stop(pair)
    print("--- Fim da Linha Reta ---")
    print("Desvio Final do Giroscópio: {:.1f}°".format(motion_sensor.tilt_angles()[0] / 10.0))

async def main():
    print("--- Teste 2: Giroscópio vs Motores ---")
    
    p_left = port.A
    p_right = port.B
    
    # Alinhamento físico inicial
    print("Alinhando motores...")
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    # Teste 1: Curva de 90 graus para a direita
    await test_rotation_with_gyro(motor_pair.PAIR_1, p_left, p_right, 90, 200)
    
    await runloop.sleep_ms(2000)
    
    # Teste 2: Andar reto por 5 segundos e ver se entorta
    await test_straight_drift(motor_pair.PAIR_1, p_left, p_right, 5000, 400)
    
    print("\nTodos os testes concluídos!")

runloop.run(main())
