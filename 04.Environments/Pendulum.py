#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pygame
import math
import numpy as np
import torch
import math
import random

class PendulumEnv:
    def __init__(self):
        self.g = 9.8  # gravitational acceleration
        self.l = 1.0  # pendulum length (m)
        self.dt = 0.02  # time step
        self.damping = 0.1  # damping coefficient

        # [angle, angular velocity]
        self.state = [math.pi / 4, 0]

        self.observation_space = 2
        self.action_space = (-2.0, 2.0)  # driving forces (torque)

        self.viewer = None

        self.success_steps = 0
        self.success_threshold = 50
        self.theta_tolerance = 0.1
        self.bottom_tolerance = 0.1

    def step(self, action):
        theta, theta_dot = self.state
        torque = np.clip(action, *self.action_space)
        theta_ddot = (-self.g / self.l) * math.sin(theta) - self.damping * theta_dot + torque / (self.l**2)
        theta += theta_dot * self.dt
        theta_dot += theta_ddot * self.dt

        self.state = [theta, theta_dot]

        reward = -abs(theta)  # Max theta = 0

        if abs(theta) < self.theta_tolerance:
            self.success_steps += 1
        else:
            self.success_steps = 0

        if abs(theta + math.pi) < self.bottom_tolerance:
            done = True
            reward = -10000
            return np.array(self.state), reward, done, {}

        done = self.success_steps >= self.success_threshold
        return np.array(self.state), reward, done, {}

    def reset(self):
        self.state = [np.random.uniform(-math.pi, math.pi), 0]
        self.success_steps = 0
        return np.array(self.state)

    def render(self, mode="human"):
        if self.viewer is None:
            pygame.init()
            self.width, self.height = 600, 600
            self.viewer = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Pendulum")

        self.viewer.fill((255, 255, 255))

        origin = (self.width // 2, self.height // 2)
        theta, _ = self.state

        pendulum_length = self.height // 3
        x = int(origin[0] + pendulum_length * math.sin(theta))
        y = int(origin[1] - pendulum_length * math.cos(theta))

        pygame.draw.line(self.viewer, (0, 0, 0), origin, (x, y), 5)
        pygame.draw.circle(self.viewer, (255, 0, 0), (x, y), 15)
        pygame.draw.circle(self.viewer, (0, 0, 0), origin, 5)

        pygame.display.flip()


    def close(self):
        if self.viewer:
            pygame.quit()
            self.viewer = None

