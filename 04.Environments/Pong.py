#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pygame
import random
import json

class PongGame:
    def __init__(self, policy_path):
        pygame.init()
        self.WIDTH, self.HEIGHT = 800, 600
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

        self.BALL_SPEED = 5
        self.OPPONENT_SPEED = 6
        self.PADDLE_WIDTH, self.PADDLE_HEIGHT = 10, 100
        self.BALL_SIZE = 15

        self.NUM_PADDLE_POS = 30
        self.NUM_BALL_X = 50
        self.NUM_BALL_Y = 40

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        self.player_score = 0
        self.opponent_score = 0

        self.player = pygame.Rect(self.WIDTH - 20, self.HEIGHT // 2 - self.PADDLE_HEIGHT // 2, self.PADDLE_WIDTH, self.PADDLE_HEIGHT)
        self.opponent = pygame.Rect(10, self.HEIGHT // 2 - self.PADDLE_HEIGHT // 2, self.PADDLE_WIDTH, self.PADDLE_HEIGHT)

        self.ball = pygame.Rect(self.WIDTH // 2, self.HEIGHT // 2, self.BALL_SIZE, self.BALL_SIZE)
        self.ball_dx = self.BALL_SPEED * random.choice([1, -1])
        self.ball_dy = self.BALL_SPEED * random.choice([1, -1])

        self.policy = self.load_policy(policy_path)

    def load_policy(self, filename):
        with open(filename, "r") as f:
            policy = json.load(f)
        return {eval(state): action for state, action in policy.items()}

    def discretize(self, value, max_value, bins):
        return min(bins - 1, max(0, int(value / max_value * bins)))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] and self.player.top > 0:
                self.player.y -= self.OPPONENT_SPEED
            if keys[pygame.K_DOWN] and self.player.bottom < self.HEIGHT:
                self.player.y += self.OPPONENT_SPEED

            # AGENT – wybór akcji z polityki
            state = (
                self.discretize(self.opponent.y, self.HEIGHT, self.NUM_PADDLE_POS),
                self.discretize(self.ball.x, self.WIDTH, self.NUM_BALL_X),
                self.discretize(self.ball.y, self.HEIGHT, self.NUM_BALL_Y),
                1 if self.ball_dx > 0 else -1,
                1 if self.ball_dy > 0 else -1
            )

            action = self.policy.get(state, 0)
            if action == -1 and self.opponent.top > 0:
                self.opponent.y -= self.OPPONENT_SPEED
            elif action == 1 and self.opponent.bottom < self.HEIGHT:
                self.opponent.y += self.OPPONENT_SPEED

            self.ball.x += self.ball_dx
            self.ball.y += self.ball_dy

            if self.ball.top <= 0 or self.ball.bottom >= self.HEIGHT:
                self.ball_dy *= -1

            if self.ball.colliderect(self.player) or self.ball.colliderect(self.opponent):
                self.ball_dx *= -1

            if self.ball.left <= 0:
                self.player_score += 1
                self.reset_ball()
            elif self.ball.right >= self.WIDTH:
                self.opponent_score += 1
                self.reset_ball()

            self.draw()

            self.clock.tick(60)
        pygame.quit()

    def reset_ball(self):
        self.ball.x, self.ball.y = self.WIDTH // 2, self.HEIGHT // 2
        self.ball_dx = self.BALL_SPEED * random.choice([1, -1])
        self.ball_dy = self.BALL_SPEED * random.choice([1, -1])

    def draw(self):
        self.screen.fill(self.BLACK)
        pygame.draw.rect(self.screen, self.WHITE, self.player)
        pygame.draw.rect(self.screen, self.WHITE, self.opponent)
        pygame.draw.ellipse(self.screen, self.WHITE, self.ball)
        pygame.draw.aaline(self.screen, self.WHITE, (self.WIDTH // 2, 0), (self.WIDTH // 2, self.HEIGHT))

        player_text = self.font.render(f"Gracz: {self.player_score}", True, self.WHITE)
        opponent_text = self.font.render(f"Agent: {self.opponent_score}", True, self.WHITE)
        self.screen.blit(player_text, (self.WIDTH - 200, 20))
        self.screen.blit(opponent_text, (20, 20))
        pygame.display.flip()

