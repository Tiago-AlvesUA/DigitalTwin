import pymunk
import pymunk.pygame_util
import pygame

# Initialize Pygame and Pymunk
pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, 0)  # No gravity for car movement

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

# Create two vehicles
car1, shape1 = create_car((100, 300), 1, 0, 50, 100,40)
car2, shape2 = create_car((100, 250), 1, 0.10, 50,50,20)  # Opposite direction

# Collision Handler (Uses GJK)
def collision_handler(arbiter, space, data):
    print("Collision detected!")
    return True

collision = space.add_collision_handler(1, 1)  # Type 1 = Cars
collision.begin = collision_handler

# Main simulation loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break

    # Step the physics simulation
    space.step(1/60)

    # Draw everything
    screen.fill((255, 255, 255))
    draw_options = pymunk.pygame_util.DrawOptions(screen)
    space.debug_draw(draw_options)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
