import math
import json
from dataclasses import dataclass
import utm
import pymunk
import pymunk.pygame_util
import pygame
import os

time_elapsed = 0.0
collision_time = None
pygame.init()
WIDTH, HEIGHT = 500, 300
window = pygame.Surface((WIDTH, HEIGHT)) # instead of pygame.display.set_mode((WIDTH, HEIGHT)) to avoid opening a window
# Surface is an image created in memory, which can be used for drawing and then saved to a file

def compass_to_trigonometric_angle(degrees_heading):
    return math.radians(90 - degrees_heading)

def apply_force(vehicle, acceleration):
    force = vehicle.mass * acceleration # F = m * a (Newton's second law)
    heading = vehicle.angle

    force_x = force * math.cos(heading)
    force_y = force * math.sin(heading)

    #vehicle.apply_impulse_at_local_point((force_x,force_y), (0,0))
    vehicle.apply_force_at_local_point((force_x,force_y), (0,0))    # Always applied at position (0,0) since it is the Center of Mass of the object (it already takes in consideration the coordinates where the object is)


def create_vehicle(space, position, mass, width, length, heading, speed, color):
    # Since pymunk does not care about length, it just draws a rectangle where width is aligned with the x-axis and height with the y-axis, we need to switch width and length
    box_width = length
    box_height = width
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, (box_width, box_height))) # Moment for box calculates moment of intertia, which is necessary to determine resistance to rotational motion (and behave more realistically)
    x, y = position
    body.position = (x,y)
    body.angle = heading
    body.color = color
    # Using initial speed to calculate velocity
    velocity_x = speed * math.cos(heading)
    velocity_y = speed * math.sin(heading)
    body.velocity = (velocity_x, velocity_y)

    # pymunk.Poly is a convex polygon shape
    shape = pymunk.Poly.create_box(body, (box_width, box_height))
    shape.mass = mass
    shape.collision_type = 1
    shape.color = pygame.Color(*color)

    space.add(body, shape)
    return body, shape

def draw(space, window, draw_options, sender_body, receiver_body):
    #window.fill("white")
    space.debug_draw(draw_options)
    # Draw heading arrows
    # draw_heading_arrow(window, sender_body, color=(0, 0, 0))   # black arrow for sender
    # draw_heading_arrow(window, receiver_body, color=(50, 50, 50))  # dark gray arrow for receiver
    # pygame.display.update() # Only needed if using pygame.display.set_mode


# Convert spherical coordinates to Universal Transverse Mercater(UTM) to use GJK via pymunk
def coordinates_to_utm(coord):
    coordUTM = utm.from_latlon(*coord)

    x = coordUTM[0] - 526186
    y = coordUTM[1] - 4497892

    print(f"x: {x} and y: {y}")

    return (x,y)


def collision_handler(arbiter, space, data):
    global collision_time, time_elapsed
    collision_time = time_elapsed
    print(f"Collision detected at {collision_time:.2f} seconds!")
    return True


def run(window, width, height):
    global time_elapsed
    #running = True
    #clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps # Each step (difference time) will be 1/60 of a second

    space = pymunk.Space()
    space.gravity = (0,0)

    #sender_position = coordinates_to_utm((40.6314509, -8.6896659)) # No collision
    sender_position = coordinates_to_utm((40.6314173, -8.6898435)) # Collision
    receiver_position = coordinates_to_utm((40.6318981, -8.6903491))

    # Headings in radians (Headings come in degrees x 10)
    sender_heading = compass_to_trigonometric_angle(2595/10)
    receiver_heading = compass_to_trigonometric_angle(2000/10)

    print(f"Headings of sender: {sender_heading} and of receiver: {receiver_heading}")

    # Sizes of the vehicles are in meters*10 (and width and length need to be switched?)
    # Speed is also in meters/second
    sender_body, sender_shape = create_vehicle(space, sender_position, 10, 1.8, 4.3, sender_heading, 2500*1e-2, color=(0, 0, 255, 255)) # blue
    receiver_body, receiver_shape = create_vehicle(space, receiver_position, 10, 1.8, 4.3, receiver_heading, 2500*1e-2, color=(255, 0, 0, 255)) # red

    collision = space.add_collision_handler(1, 1)  # Type 1 = Cars
    collision.begin = collision_handler

    draw_options = pymunk.pygame_util.DrawOptions(window)
    # Flip Y-axis, since pygame origin is at the top left corner
    # Also, translate the origin to the center of the screen
    flip_y = pymunk.Transform(a=1, b=0, c=0, d=-1, tx=WIDTH // 2, ty=HEIGHT // 2)
    draw_options.transform = flip_y


    for _ in range(300):
        draw(space, window, draw_options, sender_body, receiver_body)

        if collision_time is not None:
            # Change color to white
            sender_shape.color = (255, 255, 255, 255)
            receiver_shape.color = (255, 255, 255, 255)
        
        space.step(dt) # Step the physics simulation
        #clock.tick(fps)
        time_elapsed += dt

    output_dir = "simulation_frames"
    os.makedirs(output_dir, exist_ok=True) # Create folder if it doesn't exist
    image_path = os.path.join(output_dir, "final_frame.jpg") # Save the last frame in the folder
    pygame.image.save(window, image_path)


if __name__ == "__main__":
    run(window, WIDTH, HEIGHT)


# def draw_heading_arrow(window, body, color=(0, 0, 0), length=30):
#     x, y = body.position
#     angle = body.angle

#     # Calculate the end of the arrow using angle and length
#     end_x = x + length * math.cos(angle)
#     end_y = y + length * math.sin(angle)

#     # Shift positions to match draw_options.transform (centered on screen)
#     start_pos = (int(x + WIDTH // 2), int(HEIGHT // 2 - y))
#     end_pos = (int(end_x + WIDTH // 2), int(HEIGHT // 2 - end_y))

#     pygame.draw.line(window, color, start_pos, end_pos, 3)  # 3 = line thickness
#     pygame.draw.circle(window, color, end_pos, 4)  # dot at the end