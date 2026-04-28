#!/usr/bin/python
#Author: Ben Prishtina
#Purpose: Semester Project
#CAP5937: ST Applied Machine Learning
import pygame
from TankGame import TankGame
import torch
from QNetwork import QNetwork

def main():
    game = TankGame(render_mode=True)
    state = game.reset()
    
    running = True

    state_dim = 4
    action_dim = 4
    q_net = QNetwork(state_dim=4, action_dim=4)
    q_net.load_state_dict(torch.load("tank_dqn.pth"))
    q_net.eval()

    while running:
        # 1. Handle Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    
        # 2. Get User Input
        keys = pygame.key.get_pressed()
        #print("TEST")
        # --- HUMAN controls player ---
        game.move_player(keys)
        
        if keys[pygame.K_SPACE]:
            game.player_shoot()
        
        # --- AI controls tank ---
        with torch.no_grad():
            state_tensor = torch.tensor(state, dtype=torch.float32)
            q_values = q_net(state_tensor)
            ai_action = torch.argmax(q_values).item()
        
        state, reward, done = game.step(ai_action)
        
#        action = None # Default: no action
#        if keys[pygame.K_LEFT]:
#            action = 0 # Turn Left
#        elif keys[pygame.K_RIGHT]:
#            action = 1 # Turn Right
#        elif keys[pygame.K_UP]:
#            action = 2 # Move Forward
#        elif keys[pygame.K_SPACE]:
#            action = 3 # Shoot
#    
#        # 3. Step the Game
#        # If action is None, the tank just sits still
#        if action is not None:
#            state, reward, done = game.step(action)
        
        # 4. Draw to Screen
        game.render()
    
    pygame.quit()

if __name__ == "__main__":
    main()
