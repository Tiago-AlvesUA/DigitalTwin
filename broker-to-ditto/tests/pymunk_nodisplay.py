import pymunk
import pymunk.pygame_util
import pygame
import utm
# Initialize Pygame and Pymunk
# pygame.init()
# screen = pygame.display.set_mode((800, 600))
# clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, 0)  # No gravity for car movement


def coordinates_to_utm():
    refpos = (40.6337703, -8.6786889)
    v1_latlon = (40.6337703, -8.6786889)
    v2_latlon = (40.6337449, -8.6786678)

    referenceUTM = utm.from_latlon(*refpos)
    coorUTM1 = utm.from_latlon(*v1_latlon)
    coorUTM2 = utm.from_latlon(*v2_latlon)

    x1 = coorUTM1[0] - referenceUTM[0]
    y1 = coorUTM1[1] - referenceUTM[1]
    x2 = coorUTM2[0] - referenceUTM[0]
    y2 = coorUTM2[1] - referenceUTM[1]

    return x1,y1,x2,y2

# Function to create a car body with physics
def create_car(position, mass, angle, speed, width, height):
    moment = pymunk.moment_for_box(mass, (width, height))

    body = pymunk.Body(mass, moment)
    body.position = position
    body.angle = angle  # Set heading angle

    shape = pymunk.Poly.create_box(body, (width, height))
    shape.elasticity = 0.5
    shape.friction = 0.5
    shape.collision_type = 1

    space.add(body, shape)

    # Convert speed and angle to velocity vector
    vx = speed * pymunk.Vec2d(1, 0).rotated(angle)
    body.velocity = vx

    return body, shape


x1,y1,x2,y2 = coordinates_to_utm()
print(x1)
print(y1)
print(x2)
print(y2)

# Create two vehicles
car1, shape1 = create_car((100, 300), 1, 0, 50, 100,40)
car2, shape2 = create_car((100, 250), 1, 0.10, 50,50,20)  # Opposite direction

time_elapsed = 0.0
collision_time = None

# Collision Handler (Uses GJK)
def collision_handler(arbiter, space, data):
    global collision_time
    collision_time = time_elapsed
    print(f"Collision detected at {collision_time:.2f} seconds!")
    return True

collision = space.add_collision_handler(1, 1)  # Type 1 = Cars
collision.begin = collision_handler


# Main simulation loop
for _ in range(500):
    space.step(1/60)
    time_elapsed += 1/60

    # Get the closest distance
    dist, point_a, point_b = get_closest_distance(shape1, shape2)
    print(f"Time: {time_elapsed:.2f}s - Closest Distance: {dist:.2f} units")

    if collision_time is not None:
       break
# running = True
# while running:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False

#     # Step the physics simulation
#     space.step(1/60)

#     # Draw everything
#     screen.fill((255, 255, 255))
#     draw_options = pymunk.pygame_util.DrawOptions(screen)
#     space.debug_draw(draw_options)
#     pygame.display.flip()
#     clock.tick(60)

# pygame.quit()

# if __name__ == "__main__":
#     main()