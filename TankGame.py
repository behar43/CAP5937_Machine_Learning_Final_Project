#Author: Ben Prishtina
#Purpose: Semester Project
#CAP5937: ST Applied Machine Learning
import pygame
import random
import math

# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
FPS = 60

class TankGame:
    def __init__(self, render_mode=True):
        pygame.init()
        self.last_shot = None
        self.render_mode = render_mode
        if self.render_mode:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.clock = pygame.time.Clock()
        
        self.reset()

    def reset(self):
        # Initial positions: [x, y, angle]
        #self.player_pos = [100, 200, 0]
        self.player_pos = [
            random.randint(50, SCREEN_WIDTH - 50),
            random.randint(50, SCREEN_HEIGHT - 50),
            0
        ]
        self.ai_pos = [500, 200, 180]
        self.done = False
        self.prev_x = self.ai_pos[0]
        self.prev_y = self.ai_pos[1]
        self.shoot_cooldown = 0
        return self._get_state()

#    def _get_state(self):
#        # This is what you feed your ML model
#        # Normalized relative positions are usually best for ML
#        rel_x = (self.player_pos[0] - self.ai_pos[0]) / SCREEN_WIDTH
#        rel_y = (self.player_pos[1] - self.ai_pos[1]) / SCREEN_HEIGHT
#        return [rel_x, rel_y, self.ai_pos[2] / 360.0]

    def _get_state(self):
        dx = self.player_pos[0] - self.ai_pos[0]
        dy = self.player_pos[1] - self.ai_pos[1]
    
        # Normalize position
        rel_x = dx / SCREEN_WIDTH
        rel_y = dy / SCREEN_HEIGHT
    
        # Distance (normalized)
        distance = math.hypot(dx, dy) / 500.0  # ~max distance
    
        # Angle from AI ? player
        target_angle = math.degrees(math.atan2(-dy, dx)) % 360
    
        # Difference between where AI is facing and where it SHOULD face
        angle_diff = (target_angle - self.ai_pos[2]) % 360
        if angle_diff > 180:
            angle_diff -= 360
    
        angle_diff /= 180.0  # normalize to [-1, 1]
    
        return [rel_x, rel_y, distance, angle_diff]

    #Action: 0=Left, 1=Right, 2=Forward, 3=Shoot
    def step(self, action):

    
        reward = 0

        movement = abs(self.ai_pos[0] - self.prev_x) + abs(self.ai_pos[1] - self.prev_y)
        #reward += 0.01 * movement


    
        # --- 1. Update AI Tank ---
        if action == 0:  # Turn Left
            self.ai_pos[2] -= 5
    
        elif action == 1:  # Turn Right
            self.ai_pos[2] += 5
    
        elif action == 2:  # Move Forward
            speed = 2
            angle_rad = math.radians(self.ai_pos[2])
    
            self.ai_pos[0] += speed * math.cos(angle_rad)
            self.ai_pos[1] -= speed * math.sin(angle_rad)
    
        elif action == 3:
            angle_rad = math.radians(self.ai_pos[2])

            shot_length = 150
            end_x = self.ai_pos[0] + shot_length * math.cos(angle_rad)
            end_y = self.ai_pos[1] - shot_length * math.sin(angle_rad)
            
            self.last_shot = ((self.ai_pos[0], self.ai_pos[1]), (end_x, end_y))

        # --- 2. Normalize Angle ---
        self.ai_pos[2] %= 360
    
        # --- 3. Keep Tank Inside Screen ---
        self.ai_pos[0] = max(0, min(SCREEN_WIDTH - 30, self.ai_pos[0]))
        self.ai_pos[1] = max(0, min(SCREEN_HEIGHT - 30, self.ai_pos[1]))
    
        # --- 4. Small Time Penalty (encourages efficiency) ---
        reward -= 0.01
    
        # --- 5. Optional: Distance-based shaping reward ---
        self.prev_x = self.ai_pos[0]
        self.prev_y = self.ai_pos[1]
        dx = self.player_pos[0] - self.ai_pos[0]
        dy = self.player_pos[1] - self.ai_pos[1]
        distance = math.hypot(dx, dy)
    
        #reward += (1.0 / (distance + 1))  # closer = better
        reward -= 0.001 * distance  # smoot gradiant
    
        # --- 6. Get new state ---
        state = self._get_state()

        # --- HIT DETECTION (always runs) ---
        dx = self.player_pos[0] - self.ai_pos[0]
        dy = self.player_pos[1] - self.ai_pos[1]
        
        distance = math.hypot(dx, dy)
        
        target_angle = math.degrees(math.atan2(-dy, dx)) % 360
        ai_angle = self.ai_pos[2] % 360
        
        angle_diff = abs(target_angle - ai_angle)
        angle_diff = min(angle_diff, 360 - angle_diff)
        
        if distance < 120 and angle_diff < 20:
            print("HIT!")
            reward = 10
            self.done = True
    
        return state, reward, self.done

    def render(self):
        if not self.render_mode: return
        
        self.screen.fill((30, 30, 30)) # Dark Grey background
        
        # Draw Player (Green)
        pygame.draw.rect(self.screen, (0, 255, 0), (*self.player_pos[:2], 30, 30))
        
        # Draw AI (Red)
        pygame.draw.rect(self.screen, (255, 0, 0), (*self.ai_pos[:2], 30, 30))

        if self.last_shot:
            pygame.draw.line(self.screen, (255, 255, 0),
                             self.last_shot[0],
                             self.last_shot[1], 2)
        
        pygame.display.flip()
        self.clock.tick(FPS)

    def move_player(self, keys):
        speed = 3
    
        if keys[pygame.K_a]:
            self.player_pos[0] -= speed
        if keys[pygame.K_d]:
            self.player_pos[0] += speed
        if keys[pygame.K_w]:
            self.player_pos[1] -= speed
        if keys[pygame.K_s]:
            self.player_pos[1] += speed
    
        # keep inside screen
        self.player_pos[0] = max(0, min(SCREEN_WIDTH - 30, self.player_pos[0]))
        self.player_pos[1] = max(0, min(SCREEN_HEIGHT - 30, self.player_pos[1]))

    def player_shoot(self):
        dx = self.ai_pos[0] - self.player_pos[0]
        dy = self.ai_pos[1] - self.player_pos[1]
    
        distance = math.hypot(dx, dy)
    
        # Assume player always shoots toward AI (simpler than rotation)
        angle_rad = math.atan2(-dy, dx)
    
        shot_length = 150
        end_x = self.player_pos[0] + shot_length * math.cos(angle_rad)
        end_y = self.player_pos[1] - shot_length * math.sin(angle_rad)
    
        # Store for rendering
        self.last_shot = ((self.player_pos[0], self.player_pos[1]), (end_x, end_y))
    
        # Hit detection (same idea as AI)
        if distance < 120:
            print("PLAYER HIT!")
            self.done = True
