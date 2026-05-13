import motor_pair
import runloop
from hub import port, motion_sensor, light_matrix, button
import utime
import motor

# --- CONFIGURAÇÕES ---
CM_TO_DEG = 20.65
PORT_LEFT = port.A
PORT_RIGHT = port.B

# --- BIBLIOTECA AVANÇADA ---

async def move_profiled(distance_cm, max_vel, accel_pct=0.2, decel_pct=0.3):
    target_deg = distance_cm * CM_TO_DEG
    motor.reset_relative_position(PORT_LEFT, 0)
    motor.reset_relative_position(PORT_RIGHT, 0)
    target_yaw = motion_sensor.tilt_angles()[0] * -0.1
    while True:
        pos = (abs(motor.relative_position(PORT_LEFT)) + abs(motor.relative_position(PORT_RIGHT))) / 2
        pct = pos / target_deg
        if pct >= 1.0: break
        v = max_vel
        if pct < accel_pct: v = 80 + (max_vel - 80) * (pct / accel_pct)
        elif pct > (1 - decel_pct): v = 80 + (max_vel - 80) * ((1 - pct) / decel_pct)
        err = target_yaw - (motion_sensor.tilt_angles()[0] * -0.1)
        while err > 180: err -= 360
        while err < -180: err += 360
        motor_pair.move(motor_pair.PAIR_1, int(err * 1.2), velocity=int(v))
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

async def turn_pd(target_angle, kp=2.5, kd=5.0):
    last_error = 0
    settle = 0
    while True:
        curr = motion_sensor.tilt_angles()[0] * -0.1
        err = target_angle - curr
        while err > 180: err -= 360
        while err < -180: err += 360
        vel = (err * kp) + ((err - last_error) * kd)
        last_error = err
        abs_v = abs(vel)
        if abs_v > 300: vel = 300 if vel > 0 else -300
        if abs_v < 40: vel = 40 if vel > 0 else -40
        if abs(err) < 0.5:
            settle += 1
            if settle > 20: break
        else: settle = 0
        motor_pair.move(motor_pair.PAIR_1, 100 if err > 0 else -100, velocity=int(abs(vel)))
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

async def move_arc(radius, target_angle, velocity):
    steering = int(500 / radius)
    while True:
        curr = motion_sensor.tilt_angles()[0] * -0.1
        err = target_angle - curr
        while err > 180: err -= 360
        while err < -180: err += 360
        if abs(err) < 3.0: break
        s = steering if err > 0 else -steering
        motor_pair.move(motor_pair.PAIR_1, s, velocity=velocity)
        await runloop.sleep_ms(10)
    motor_pair.stop(motor_pair.PAIR_1)

# --- MISSÕES ---

async def m7(): await move_profiled(50, 300, 0.1, 0.1)
async def m8(): await turn_pd(90)
async def m9():
    for a in range(0, 91, 10): await turn_pd(a, 1.5, 2.0)
async def m10(): await move_profiled(80, 500, 0.2, 0.3)
async def m11(): await move_arc(25, 90, 300)
async def m12():
    for a in [15, 30, 45, 90]: 
        await turn_pd(a); await runloop.sleep_ms(500)
    await turn_pd(0)
async def m13():
    for i in range(1, 13): await turn_pd((i*30)%360)
async def m14():
    await move_profiled(30, 300); await turn_pd(45)
    await turn_pd(0); await move_profiled(30, 300)
async def m15():
    await move_arc(20, 180, 250); await move_arc(20, 0, 250)

# --- MAIN ---

async def main():
    motor_pair.pair(motor_pair.PAIR_1, PORT_LEFT, PORT_RIGHT)
    idx = 7
    while True:
        light_matrix.write(str(idx))
        if button.pressed(button.LEFT):
            idx = 7 if idx == 7 else idx - 1
            await runloop.sleep_ms(250)
        elif button.pressed(button.RIGHT):
            idx = 15 if idx == 15 else idx + 1
            await runloop.sleep_ms(250)
        if button.pressed(button.CONNECT):
            light_matrix.show_image(light_matrix.IMAGE_ARROW_N)
            if idx == 7: await m7()
            elif idx == 8: await m8()
            elif idx == 9: await m9()
            elif idx == 10: await m10()
            elif idx == 11: await m11()
            elif idx == 12: await m12()
            elif idx == 13: await m13()
            elif idx == 14: await m14()
            elif idx == 15: await m15()
            light_matrix.show_image(light_matrix.IMAGE_YES)
            await runloop.sleep_ms(1000)
        await runloop.sleep_ms(50)

runloop.run(main())
