import math
import utm
import pymunk
import pymunk.pygame_util
import pygame

time_elapsed = 0.0
collision_time = None

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Convert spherical coordinates to Universal Transverse Mercater(UTM) to use GJK via pymunk
def coordinates_to_utm(coord, refCoord):
    referenceUTM = utm.from_latlon(*refCoord)
    coordUTM = utm.from_latlon(*coord)

    x = coordUTM[0] - referenceUTM[0]
    y = coordUTM[1] - referenceUTM[1]

    print(f"x: {x} and y: {y}")

    return x,y

def create_simulation_vehicle(space, position, mass, angle, speed, width, length):
    moment = pymunk.moment_for_box(mass, (width, length))

    body = pymunk.Body(mass, moment)
    body.position = position
    body.angle = angle # heading angle

    shape = pymunk.Poly.create_box(body, (width, length))
    shape.collision_type = 1

    space.add(body, shape)

    # Conver speed and angle(heading) to velocity vector
    # angle must be in radians
    vx = speed * pymunk.Vec2d(1,0).rotated(angle)
    body.velocity = vx

    return body, shape

def collision_handler(arbiter, space, data):
    global collision_time, time_elapsed
    collision_time = time_elapsed
    print(f"Collision detected at {collision_time:.2f} seconds!")
    return True

def check_collisions():
    global collision_time, time_elapsed
    space = pymunk.Space()
    space.gravity = (0,0)
    time_elapsed = 0.0
    collision_time = None

    collision_detected = False
    #406313846, -86900170
    # Transform spherical coordinates into UTM ones (plane). TODO: Must get reference position from the receiver to serve as normalizer
    sender_x,sender_y = coordinates_to_utm((40.6314060, -8.6899038), (40.6318981, -8.6903491))
    receiver_x,receiver_y = coordinates_to_utm((40.6318981, -8.6903491),(40.6318981, -8.6903491))
# 40.631774, -8.690393
    #print(f"Sender coordinates: {sender_x}, {sender_y}")
    #print(f"Receiver coordinates:  {receiver_x}, {receiver_y}")

    # def create_car(position, mass, angle, speed, width, height):
    # heading comes in centidegrees, so convert it to radians
    heading_radians_sender = math.radians(2595 / 100)
    heading_radians_receiver = math.radians(2000/100)

    print(f"Headings of sender: {heading_radians_sender} and of receiver: {heading_radians_receiver}")

    # TODO: Check how i should introduce speed for the simulated vehicle
    sender_vehicle, sender_shape = create_simulation_vehicle(space, (sender_x,sender_y), 1, heading_radians_sender, 2500*1e-2, 18, 43) # ...width, height) ??
    receiver_vehicle, receiver_shape = create_simulation_vehicle(space, (receiver_x,receiver_y), 1, heading_radians_receiver, 2501*1e-2, 18, 43)

    collision = space.add_collision_handler(1, 1)  # Type 1 = Cars
    collision.begin = collision_handler

    draw_options = pymunk.pygame_util.DrawOptions(screen)
    # Since .step accepts seconds, each step s 1/60th of a second, meaning the checking for collision goes on for 10 seconds (600/60)
    for _ in range(600):
        space.step(1/60)
        time_elapsed += 1/60

        # if collision_time is not None:
        #     collision_detected = True
        #     break

        # Draw everything
        screen.fill((255, 255, 255))
        draw_options = pymunk.pygame_util.DrawOptions(screen)
        space.debug_draw(draw_options)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    return collision_detected


def main():
    collision_encountered = check_collisions()
    # if (collision_encountered):
    #     print("Yes, collision")
    # else:
    #     print("No, nothing detected")

if __name__ == "__main__":
    main()