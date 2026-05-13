import motor_pair
import runloop
from hub import port
import utime
import motor

async def move_with_profile(pair, left_port, right_port, duration_ms, max_velocity, reverse=False):
    """
    Move the robot with a smooth acceleration and deceleration profile,
    while monitoring motor positions for comparison.
    """
    # Reseta a posição relativa para começar do zero
    motor.reset_relative_position(left_port, 0)
    motor.reset_relative_position(right_port, 0)
    
    start_time = utime.ticks_ms()
    last_print = 0
    
    accel_time = duration_ms * 0.2
    decel_time = duration_ms * 0.2
    direction = -1 if reverse else 1
    
    while True:
        current_time = utime.ticks_ms()
        elapsed = utime.ticks_diff(current_time, start_time)
        
        if elapsed >= duration_ms:
            break
            
        # Cálculo da velocidade
        if elapsed < accel_time:
            velocity = max_velocity * (elapsed / accel_time)
        elif elapsed > (duration_ms - decel_time):
            remaining_time = duration_ms - elapsed
            velocity = max_velocity * (remaining_time / decel_time)
        else:
            velocity = max_velocity
        
        velocity *= direction
        motor_pair.move(pair, 0, velocity=int(velocity))
        
        # Monitoramento: Lê a posição de cada motor
        pos_left = motor.relative_position(left_port)
        pos_right = motor.relative_position(right_port)
        diff = pos_left - pos_right
        
        # Imprime os dados a cada 250ms para não sobrecarregar o console
        if utime.ticks_diff(current_time, last_print) > 250:
            print("Time: {}ms | L: {} | R: {} | Diff: {}".format(elapsed, pos_left, pos_right, diff))
            last_print = current_time
        
        await runloop.sleep_ms(20)

    # Parada final e relatório
    motor_pair.stop(pair)
    final_l = motor.relative_position(left_port)
    final_r = motor.relative_position(right_port)
    print("--- Fim do Movimento ---")
    print("Posição Final - Esq: {}, Dir: {}, Erro Total: {}".format(final_l, final_r, final_l - final_r))

async def main():
    print("--- Teste de Sincronia de Motores ---")
    
    # Portas definidas aqui
    p_left = port.A
    p_right = port.B
    
    # 1. Alinhamento inicial: Retornar para a posição absoluta 0
    print("Alinhando motores na posição 0...")
    # Movemos os dois em sequência para garantir o alinhamento físico (marcas do motor)
    await motor.run_to_absolute_position(p_left, 0, 300)
    await motor.run_to_absolute_position(p_right, 0, 300)
    print("Motores alinhados.")
    
    # 2. Configurar o par de motores
    motor_pair.pair(motor_pair.PAIR_1, p_left, p_right)
    
    print("Iniciando monitoramento (10s para frente)...")
    await move_with_profile(motor_pair.PAIR_1, p_left, p_right, 10000, 500, reverse=False)
    
    await runloop.sleep_ms(1000)
    
    print("Iniciando monitoramento (10s para trás)...")
    await move_with_profile(motor_pair.PAIR_1, p_left, p_right, 10000, 500, reverse=True)
    
    print("Teste concluído!")

runloop.run(main())
