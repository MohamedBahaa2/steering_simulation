import pygame
import sys
import math

pygame.init()
screen_width, screen_height = 800, 600  # Default size, can be resized
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
clock = pygame.time.Clock()

# Car dimensions
TW = 1.2  # meters (width of the car)
WB = 2.0  # meters (length of the car)
PIXELS_PER_METER = 100  # Scale factor for conversion

class SteeringSystem:
    def __init__(self, turn_radius, speed):
        self.turn_radius = turn_radius  # meters
        self.speed = speed  # pixels per frame
        self.angle = 0  # vehicle's heading angle in radians
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.x = self.center_x + self.turn_radius * PIXELS_PER_METER
        self.y = self.center_y
        self.wheel_angle = 0
        self.inner_wheel_angle = 0
        self.outer_wheel_angle = 0
        self.tilt_angle = 0  # Tilt angle of the car
        self.zoom_level = 1.0  # Zoom level

    def update(self):
        if self.turn_radius > 0:
            # Update angle
            self.angle += self.speed / self.turn_radius / PIXELS_PER_METER  # Update angle in radians
            
            # Calculate new position
            self.x = self.center_x + self.turn_radius * PIXELS_PER_METER * self.zoom_level * math.cos(self.angle)
            self.y = self.center_y + self.turn_radius * PIXELS_PER_METER * self.zoom_level * math.sin(self.angle)
            
            # Keep the car within screen bounds
            self.x = max(0, min(self.x, screen_width))
            self.y = max(0, min(self.y, screen_height))
            
            # Calculate the steering angles
            outer_steering_angle = math.atan2(WB, self.turn_radius)  # Outer wheel angle in radians
            inner_steering_angle = math.atan2(WB, self.turn_radius - TW)  # Inner wheel angle in radians
            
            self.outer_wheel_angle = math.degrees(outer_steering_angle)  # Convert to degrees
            self.inner_wheel_angle = math.degrees(inner_steering_angle)  # Convert to degrees

            # Update tilt angle
            self.tilt_angle = -math.degrees(math.atan2(self.y - self.center_y, self.x - self.center_x))
        else:
            # If the turn radius is zero, move in a straight line
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
            
            # Keep the car within screen bounds
            self.x = max(0, min(self.x, screen_width))
            self.y = max(0, min(self.y, screen_height))
            
            self.outer_wheel_angle = 0  # Reset wheel angle when moving straight
            self.inner_wheel_angle = 0
            self.tilt_angle = 0  # Reset tilt angle when moving straight

    def draw(self):
        screen.fill((255, 255, 255))  # White background
        
        # Draw the vehicle as a rectangle with tilt effect
        car_surface = pygame.Surface((int(TW * PIXELS_PER_METER * self.zoom_level), int(WB * PIXELS_PER_METER * self.zoom_level)), pygame.SRCALPHA)
        pygame.draw.rect(car_surface, (0, 0, 255), car_surface.get_rect())  # Draw car
        rotated_surface = pygame.transform.rotate(car_surface, self.tilt_angle)  # Rotate according to the tilt angle
        car_rect = rotated_surface.get_rect(center=(self.x, self.y))
        screen.blit(rotated_surface, car_rect.topleft)
        
        # Draw the fixed point in the middle of the screen
        fixed_point = (self.center_x, self.center_y)
        pygame.draw.circle(screen, (255, 0, 0), fixed_point, 5)  # Fixed point, size not affected by zoom
        
        # Draw the rigid line from the fixed point to car center, length proportional to turn radius and zoom level
        pygame.draw.line(screen, (0, 255, 0), fixed_point, (self.x, self.y), int(2 * self.zoom_level))  # Line thickness scales with zoom
        
        # Draw the turn radius slider
        pygame.draw.rect(screen, (0, 0, 0), (0, screen_height - 60, screen_width, 20))  # Slider track
        slider_pos = min(max(self.turn_radius * PIXELS_PER_METER, 0), screen_width - 20)
        pygame.draw.rect(screen, (255, 0, 0), (slider_pos, screen_height - 60, 20, 20))  # Slider knob
        
        # Draw zoom control buttons
        pygame.draw.rect(screen, (0, 255, 0), (50, screen_height - 300, 100, 40))  # Zoom in button
        pygame.draw.rect(screen, (255, 0, 0), (50, screen_height - 360, 100, 40))  # Zoom out button
        
        # Draw speed control buttons
        pygame.draw.rect(screen, (0, 255, 0), (50, screen_height - 420, 100, 40))  # Increase speed button
        pygame.draw.rect(screen, (255, 0, 0), (50, screen_height - 480, 100, 40))  # Decrease speed button
        
        # Draw wheel angles indicator
        pygame.draw.line(screen, (0, 0, 0), (screen_width - 50, screen_height - 50), (screen_width - 50, screen_height - 50 - self.outer_wheel_angle * 2), 2)  # Outer wheel indicator
        pygame.draw.line(screen, (0, 0, 0), (screen_width - 50, screen_height - 50), (screen_width - 50, screen_height - 50 + self.inner_wheel_angle * 2), 2)  # Inner wheel indicator
        
        # Draw the turn radius text
        if self.turn_radius > 0:
            font = pygame.font.SysFont(None, 24)
            radius_text = font.render(f'Radius: {self.turn_radius:.2f}', True, (0, 0, 0))
            screen.blit(radius_text, (self.x + 10, self.y - 30))
        
        # Draw text
        font = pygame.font.SysFont(None, 24)
        text = font.render(f"Turn Radius: {self.turn_radius:.2f}", True, (0, 0, 0))
        screen.blit(text, (50, screen_height - 80))
        text = font.render(f"Inner Wheel Angle: {self.outer_wheel_angle:.2f}", True, (0, 0, 0))
        screen.blit(text, (50, screen_height - 120))
        text = font.render(f"Outer Wheel Angle: {self.inner_wheel_angle:.2f}", True, (0, 0, 0))
        screen.blit(text, (50, screen_height - 160))
        text = font.render(f"Speed: {self.speed:.2f}", True, (0, 0, 0))
        screen.blit(text, (50, screen_height - 200))
        text = font.render(f"Zoom: {self.zoom_level:.2f}", True, (0, 0, 0))
        screen.blit(text, (50, screen_height - 240))
        
        # Draw button labels
        zoom_in_text = font.render("Zoom In", True, (0, 0, 0))
        screen.blit(zoom_in_text, (100 - zoom_in_text.get_width() // 2, screen_height - 280 - zoom_in_text.get_height() // 2))
        zoom_out_text = font.render("Zoom Out", True, (0, 0, 0))
        screen.blit(zoom_out_text, (100 - zoom_out_text.get_width() // 2, screen_height - 340 - zoom_out_text.get_height() // 2))
        speed_up_text = font.render("Speed +", True, (0, 0, 0))
        screen.blit(speed_up_text, (100 - speed_up_text.get_width() // 2, screen_height - 400 - speed_up_text.get_height() // 2))
        speed_down_text = font.render("Speed -", True, (0, 0, 0))
        screen.blit(speed_down_text, (100 - speed_down_text.get_width() // 2, screen_height - 460 - speed_down_text.get_height() // 2))

        pygame.display.flip()

def handle_keyboard_events(event, steering_system):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            steering_system.turn_radius -= 0.1  # Decrease turn radius
        elif event.key == pygame.K_RIGHT:
            steering_system.turn_radius += 0.1  # Increase turn radius
        elif event.key == pygame.K_UP:
            steering_system.zoom_level *= 1.1  # Zoom in
        elif event.key == pygame.K_DOWN:
            steering_system.zoom_level *= 0.9  # Zoom out

        # Ensure turn_radius and zoom_level are within reasonable ranges
        steering_system.turn_radius = max(steering_system.turn_radius, 0.1)  # Prevent turn radius from being zero or negative
        steering_system.zoom_level = max(min(steering_system.zoom_level, 5.0), 0.1)  # Limit zoom level

def handle_mouse_events(event, steering_system):
    if event.type == pygame.MOUSEBUTTONDOWN:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Turn radius slider
        if screen_height - 60 <= mouse_y <= screen_height - 40:
            steering_system.turn_radius = max(0.1, mouse_x / PIXELS_PER_METER)  # Adjust turn radius based on slider position
        
        # Zoom in button
        if 50 <= mouse_x <= 150 and screen_height - 300 <= mouse_y <= screen_height - 260:
            steering_system.zoom_level *= 1.1  # Zoom in
        
        # Zoom out button
        elif 50 <= mouse_x <= 150 and screen_height - 360 <= mouse_y <= screen_height - 320:
            steering_system.zoom_level *= 0.9  # Zoom out
        
        # Increase speed button
        if 50 <= mouse_x <= 150 and screen_height - 420 <= mouse_y <= screen_height - 380:
            steering_system.speed += 1
        
        # Decrease speed button
        elif 50 <= mouse_x <= 150 and screen_height - 480 <= mouse_y <= screen_height - 440:
            steering_system.speed = max(0, steering_system.speed - 1)

        # Ensure speed and zoom_level are within reasonable ranges
        steering_system.speed = max(steering_system.speed, 0.1)  # Prevent speed from being zero or negative
        steering_system.zoom_level = max(min(steering_system.zoom_level, 5.0), 0.1)  # Limit zoom level

steering_system = SteeringSystem(turn_radius=5, speed=2)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        handle_keyboard_events(event, steering_system)
        handle_mouse_events(event, steering_system)

    # Adjust screen size if it has changed
    screen_width, screen_height = pygame.display.get_surface().get_size()
    steering_system.center_x = screen_width // 2
    steering_system.center_y = screen_height // 2

    steering_system.update()
    steering_system.draw()
    clock.tick(60)  # Limit the frame rate to 60 FPS
