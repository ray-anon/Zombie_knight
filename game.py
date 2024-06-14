import pygame , random

vector = pygame.math.Vector2

#initiliaze
pygame.init()

#set display surfaces tile - 32 x 32
WINDOW_WIDTH = 1280 #40 tiles
WINDOW_HEIGHT = 736 #23 tiles
display_surface = pygame.display.set_mode(( WINDOW_WIDTH , WINDOW_HEIGHT))
pygame.display.set_caption("Zombie arcade")

#set FPS and clock
FPS = 60
clock = pygame.time.Clock()

#define classes
class Game():
    def __init__(self , player , zombie_group , platform_group , portal_group , bullet_group , ruby_group):
        self.STARTING_ROUND_TIME = 30
        self.STARTING_ZOMBIE_CREATION_TIME = 5
        #set game values
        self.score = 0
        self.round_number = 1
        self.frame_count = 0
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME
        #set font
        self.title_font  = pygame.font.Font('fonts/Poultrygeist.ttf' , 48)
        self.HUD_font = pygame.font.Font('fonts/Pixel.ttf' , 24)

        self.player = player
        self.zombie_group = zombie_group
        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group
        self.ruby_group = ruby_group

        #sound
        self.lost_ruby_sound = pygame.mixer.Sound('sounds/lost_ruby.wav')
        self.ruby_pickup_sound = pygame.mixer.Sound('sounds/ruby_pickup.wav')
        pygame.mixer.music.load('sounds/battleThemeA.mp3')


    def update(self):
        #update round time
        self.frame_count += 1
        if self.frame_count % FPS == 0:
            self.round_time -= 1
            self.frame_count = 0
        self.check_collisions()
        self.add_zombie()
        self.check_round_completion()
        self.check_game_over()


    def draw(self):
        #set colors
        WHITE = (255 , 255 , 255)
        GREEN = (25 , 200 , 25)

        #set text
        score_text = self.HUD_font.render('Score: ' + str(self.score) , 1 , WHITE )
        score_rect = score_text.get_rect()
        score_rect.topleft = (10 , WINDOW_HEIGHT - 50)

        health_text = self.HUD_font.render('Health'  + str(self.player.health) , 1 , WHITE)
        health_rect = health_text.get_rect()
        health_rect.topleft = (10 , WINDOW_HEIGHT - 25)

        title_text = self.title_font.render('Zombie Knight' , 1, WHITE)
        title_rect = title_text.get_rect()
        title_rect.center = (WINDOW_WIDTH // 2 , WINDOW_HEIGHT - 25)

        round_text = self.HUD_font.render("Night: " + str(self.round_number) , 1 , WHITE)
        round_rect = round_text.get_rect()
        round_rect.topright = (WINDOW_WIDTH - 10 , WINDOW_HEIGHT - 50)

        time_text = self.HUD_font.render("Sunrise In: " + str(self.round_time) , 1, WHITE)
        time_rect = time_text.get_rect()
        time_rect.topright = (WINDOW_WIDTH -10 , WINDOW_HEIGHT - 25)

        #draw the texts
        display_surface.blit(score_text , score_rect)
        display_surface.blit(health_text , health_rect)
        display_surface.blit(title_text , title_rect)
        display_surface.blit(round_text , round_rect)
        display_surface.blit(time_text , time_rect)


    def add_zombie(self):
        #check to add zombie every second

        if self.frame_count % FPS == 0:
            if self.round_time % self.zombie_creation_time == 0:
                zombie = Zombie(self.platform_group , self.portal_group , self.round_number , self.round_number + 5)
                self.zombie_group.add(zombie)

    def check_collisions(self):
        collision_dict = pygame.sprite.groupcollide(self.bullet_group , self.zombie_group , True , False)
        if collision_dict:
            for zombies in collision_dict.values():
                for zombie in zombies:
                    zombie.hit_sound.play()
                    zombie.is_dead = True
                    zombie.animate_death = True
        #see player stomped a dead zombie || alive zombie
        collision_list = pygame.sprite.spritecollide(self.player , self.zombie_group , False)
        if collision_list:
            for zombie in collision_list:
                if zombie.is_dead:
                    zombie.kick_sound.play()
                    zombie.kill()
                    self.score += 25

                    ruby = Ruby(self.platform_group , self.portal_group)
                    self.ruby_group.add(ruby)
                #zombie is alive
                else:
                    self.player.health -= 20
                    self.player.hit_sound.play()
                    self.player.position.x -= 256 * zombie.direction
                    self.player.rect.bottomleft = self.player.position
        
        #player and ruby
        if pygame.sprite.spritecollide(self.player , self.ruby_group , True):
            self.ruby_pickup_sound.play()
            self.score += 100
            self.player.health += 10
            if self.player.health > self.player.STARTING_HEALTH:
                self.player.health = self.player.STARTING_HEALTH
        
        #alive zombie and ruby
        for zombie in self.zombie_group:
            if zombie.is_dead == False:
                if pygame.sprite.spritecollide(zombie , self.ruby_group , True):
                    self.lost_ruby_sound.play()
                    zombie = Zombie(self.platform_group , self.portal_group , self.round_number , self.round_number + 5)
                    self.zombie_group.add(zombie)
        


    def check_round_completion(self):
        if self.round_time == 0:
            self.start_new_round()

    def check_game_over(self):
        if self.player.health <= 0:
            pygame.mixer.music.stop()
            self.pause_game("Game over final Score " + str(self.score) , "Press enter to play again")
            self.reset_game()

    def start_new_round(self):
        
        self.round_number += 1

        if self.round_number < self.STARTING_ZOMBIE_CREATION_TIME:
            self.zombie_creation_time -= 1
        
        self.round_time  = self.STARTING_ROUND_TIME

        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        self.player.reset()
        self.pause_game("You survived the nightu" , "Continue")




    def pause_game(self , main_text , sub_text):
        global running

        pygame.mixer.music.pause()

        #set colors
        WHITE = (255 , 255 ,255)
        BLACK = (0, 0, 0 )
        GREEN = (25 , 200 ,25)

        #creat text
        main_text = self.title_font.render(main_text , 1 , GREEN)
        main_rect = main_text.get_rect()
        main_rect.center = (WINDOW_WIDTH // 2 , WINDOW_HEIGHT //2)

        sub_text = self.title_font.render(sub_text , 1, WHITE)
        sub_rect = sub_text.get_rect()
        sub_rect.center = (WINDOW_WIDTH // 2 , WINDOW_HEIGHT // 2 + 64)

        display_surface.fill((BLACK))
        display_surface.blit(main_text , main_rect)
        display_surface.blit(sub_text , sub_rect)
        pygame.display.update()

        is_paused = True
        while is_paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        is_paused = False
                        pygame.mixer.music.unpause()
                if event.type == pygame.QUIT:
                    is_paused = False
                    running = False

    def reset_game(self):
        #reset every fucking thing

        self.score = 0
        self.round_number = 1
        self.round_time = self.STARTING_ROUND_TIME
        self.zombie_creation_time = self.STARTING_ZOMBIE_CREATION_TIME

        self.player.health = self.player.STARTING_HEALTH
        self.player.reset()

        self.zombie_group.empty()
        self.ruby_group.empty()
        self.bullet_group.empty()

        pygame.mixer.music.play(-1 , 0.0)

class Tile(pygame.sprite.Sprite):
    def __init__(self , x , y , image_int , main_group , sub_group=""):
        super().__init__()
        #load images 
        #dirt tiles
        if image_int == 1:
            self.image = pygame.transform.scale(pygame.image.load('images/tiles/Tile (1).png') , (32 , 32))
        #platform tiles
        elif image_int == 2:
            self.image = pygame.transform.scale(pygame.image.load('images/tiles/Tile (2).png') , (32 , 32))
            sub_group.add(self)
        elif image_int == 3:
            self.image = pygame.transform.scale(pygame.image.load('images/tiles/Tile (3).png') , (32 , 32))
            sub_group.add(self)
        elif image_int == 4:
            self.image = pygame.transform.scale(pygame.image.load('images/tiles/Tile (4).png') , (32 , 32))
            sub_group.add(self)
        elif image_int == 5:
            self.image = pygame.transform.scale(pygame.image.load('images/tiles/Tile (5).png') , (32 , 32))
            sub_group.add(self)
        

        main_group.add(self)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x , y)

        #creating sprite masks
        self.mask = pygame.mask.from_surface(self.image)


class Player(pygame.sprite.Sprite):
    def __init__(self , x , y , platform_group , portal_group , bullet_group):
        super().__init__()

        #self constant variables
        self.HORIZONTAL_ACCELERATION = 2
        self.HORIZONTAL_FRICTION = 0.15
        self.VERTICAL_ACCELERATION = 0.8
        self.VERTICAL_JUMP_SPEED = 18
        self.STARTING_HEALTH = 100

        #animation lists
        self.move_right_sprites = []
        self.move_left_sprites = []
        self.idle_right_sprites = []
        self.idle_left_sprites = []
        self.jump_right_sprites = []
        self.jump_left_sprites = []
        self.attack_right_sprites = []
        self.attack_left_sprites = []

        for i in range(1 , 11):
            self.move_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/player/run/Run ({i}).png') , (64 , 64)))
            self.move_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/player/run/Run ({i}).png') , (64 , 64)) , True , False))
            self.idle_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/player/idle/Idle ({i}).png') , (64 , 64)))
            self.idle_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/player/idle/Idle ({i}).png') , (64 , 64)) , True , False))
            self.jump_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/player/jump/Jump ({i}).png') , (64 , 64)))
            self.jump_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/player/jump/Jump ({i}).png') , (64 , 64)) , True , False))
            self.attack_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/player/attack/Attack ({i}).png') , (64 , 64)))
            self.attack_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/player/attack/Attack ({i}).png') , (64 , 64)) , True , False))
        
        self.current_sprite = 0
        self.image = self.idle_right_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x , y)
        

        self.platform_group = platform_group
        self.portal_group = portal_group
        self.bullet_group = bullet_group

        #animation booleans
        self.animate_jump = False
        self.animate_fire = False

        #load sounds
        self.jump_sound = pygame.mixer.Sound('sounds/jump_sound.wav')
        self.slash_sound = pygame.mixer.Sound('sounds/portal_sound.wav')
        self.portal_sound = pygame.mixer.Sound('sounds/portal_sound.wav')
        self.hit_sound = pygame.mixer.Sound('sounds/player_hit.wav')


        #kinmeatics  vect
        self.position = vector(x , y)
        self.velocity = vector(0, 0)
        self.acceleration = vector(0 , self.VERTICAL_ACCELERATION)

        #set player initial values
        self.health = self.STARTING_HEALTH
        self.starting_x = x
        self.starting_y = y
    
    def update(self):
        self.move()
        self.check_collisions()
        self.check_animation()
        self.mask = pygame.mask.from_surface(self.image)


        mask_outline = self.mask.outline()
        pygame.draw.lines(self.image , (255 , 0, 0) , True , mask_outline)


    def move(self):
        #set acceleration vector

        self.acceleration = vector(0 , self.VERTICAL_ACCELERATION)

        #if keys are pressed
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            self.acceleration.x = -1 * self.HORIZONTAL_ACCELERATION
            self.animate(self.move_left_sprites , .5)
        elif key[pygame.K_RIGHT]:
            self.acceleration.x = self.HORIZONTAL_ACCELERATION
            self.animate(self.move_right_sprites , .5)
        else:
            if self.velocity.x > 0:
                self.animate(self.idle_right_sprites , .5)
            else:
                self.animate(self.idle_left_sprites , .5)
        
        self.acceleration.x -= self.velocity.x*self.HORIZONTAL_FRICTION
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        #update rect of the player image when he touches the boundary
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0
        
        self.rect.bottomleft = self.position


    def check_collisions(self):
        if self.velocity.y > 0:
            collided_platforms = pygame.sprite.spritecollide(self ,self.platform_group , False , pygame.sprite.collide_mask)
            if collided_platforms:
                self.position.y = collided_platforms[0].rect.top + 5
                self.velocity.y = 0
        #jumping up
        if self.velocity.y < 0:
            collided_platforms = pygame.sprite.spritecollide(self , self.platform_group , False , pygame.sprite.collide_mask)
            if collided_platforms:
                self.velocity.y = 0
                while pygame.sprite.spritecollide(self , self.platform_group , False):
                    self.position.y += 1
                    self.rect.bottomleft = self.position 

        #portal collisons
        if pygame.sprite.spritecollide(self , self.portal_group , False):
            self.portal_sound.play()

            if self.position.x > WINDOW_WIDTH // 2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150

            if self.position.y > WINDOW_HEIGHT // 2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 134   

    def check_animation(self):
        if self.animate_jump:
            if self.velocity.x > 0:
                self.animate(self.jump_right_sprites , .1)
            else:
                self.animate(self.jump_left_sprites , .1)
        
        #animate slash
        if self.animate_fire:
            if self.velocity.x > 0:
                self.animate(self.attack_right_sprites , .25)
            else:
                self.animate(self.attack_left_sprites , .25)


    def jump(self):
        #jumping up
        collided_platforms = pygame.sprite.spritecollide(self , self.platform_group , False)
        if collided_platforms:
            self.velocity.y = -1 * self.VERTICAL_JUMP_SPEED
            self.jump_sound.play()
            self.animate_jump = True

    def fire(self):
        self.slash_sound.play()
        Bullet(self.rect.centerx , self.rect.centery , self.bullet_group , self)
        self.animate_fire = True

    def reset(self):
        self.velocity = vector(0 ,0)
        self.position = vector(self.starting_x , self.starting_y)
        self.rect.bottomleft = self.position
        

    def animate(self , sprites_list , speed):
        if self.current_sprite < len(sprites_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            if self.animate_jump:
                self.animate_jump = False 
            if self.animate_fire:
                self.animate_fire = False
        
        self.image = sprites_list[int(self.current_sprite)]


class Bullet(pygame.sprite.Sprite):
    def __init__(self , x , y, bullet_group , player):
        super().__init__()

        #set constant variables
        self.VELOCITY = 20
        self.RANGE = 500

        #load image 
        if player.velocity.x > 0:
            self.image = pygame.transform.scale(pygame.image.load('images/player/slash.png') , (32 , 32))
        else:
            self.image = pygame.transform.scale(pygame.transform.flip(pygame.image.load('images/player/slash.png') , True , False) , (32 , 32))
            self.VELOCITY = -1 * self.VELOCITY
        
        self.rect = self.image.get_rect()
        self.rect.center = (x , y)
        self.starting_x = x
        
        bullet_group.add(self)



    def update(self):
        self.rect.x += self.VELOCITY

        if abs(self.rect.x - self.starting_x) > self.RANGE:
            self.kill()


class Zombie(pygame.sprite.Sprite):
    def __init__(self , platform_group , portal_group , min_speed , max_speed):
        super().__init__()

        #set constant variables
        self.VERTICAL_ACCELERATION = 3
        self.RISE_TIME = 2
        
        #Animation frames
        self.walk_right_sprites = []
        self.walk_left_sprites = []
        self.die_right_sprites= []
        self.die_left_sprites = []
        self.rise_right_sprites = []
        self.rise_left_sprites = []

        gender = random.randint(0, 1)
        if gender == 0:
            for i in range(1 , 11):
                self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/zombie/boy/walk/Walk ({i}).png') , (64 , 64)))
                self.walk_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/zombie/boy/walk/Walk ({i}).png') , (64 , 64)), True , False ))
                self.die_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/zombie/boy/dead/Dead ({i}).png') , (64 , 64)))
                self.die_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/zombie/boy/dead/Dead ({11 - i}).png') , (64 , 64)) , True , False))
                self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/zombie/boy/dead/Dead ({i}).png') , (64 , 64)))
                self.rise_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/zombie/boy/dead/Dead ({11 - i}).png') , (64 , 64)) , True , False))
        else:
            for i in range(1 , 11):
                self.walk_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/zombie/girl/walk/Walk ({i}).png') , (64 , 64)))
                self.walk_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/zombie/girl/walk/Walk ({i}).png') , (64 , 64)), True , False ))
                self.die_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/zombie/girl/dead/Dead ({i}).png') , (64 , 64)))
                self.die_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/zombie/girl/dead/Dead ({11 - i}).png') , (64 , 64)) , True , False))
                self.rise_right_sprites.append(pygame.transform.scale(pygame.image.load(f'images/zombie/girl/dead/Dead ({i}).png') , (64 , 64)))
                self.rise_left_sprites.append(pygame.transform.flip(pygame.transform.scale(pygame.image.load(f'images/zombie/girl/dead/Dead ({11 - i}).png') , (64 , 64)) , True , False))

        #load an image
        self.direction =  random.choice([-1 , 1])

        self.current_sprite = 0
        if self.direction == -1:
            self.image = self.walk_left_sprites[self.current_sprite]
        else:
            self.image = self.walk_right_sprites[self.current_sprite]
        
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (random.randint(100 , WINDOW_WIDTH) , -100)

        #attach sprite group
        self.platform_group = platform_group
        self.portal_group = portal_group

        #animation boolean
        self.animate_death = False
        self.animate_rise = False

        #load sound
        self.hit_sound =  pygame.mixer.Sound('sounds/zombie_hit.wav')
        self.kick_sound = pygame.mixer.Sound('sounds/zombie_kick.wav')
        self.portal_sound = pygame.mixer.Sound('sounds/portal_sound.wav')

        #kinematics
        self.position = vector(self.rect.x , self.rect.y)
        self.velocity = vector(self.direction * random.randint(min_speed , max_speed) , 0)
        self.acceleration = vector(0, self.VERTICAL_ACCELERATION)

        #initial zombie values
        self.is_dead = False
        self.round_time = 0
        self.frame_count = 0
    def update(self):
        self.move()
        self.check_animation()
        self.check_collisions()

        if self.is_dead:
            self.frame_count += 1
            if self.frame_count % FPS == 0:
                self.round_time += 1
                if self.round_time == self.RISE_TIME:
                    self.animate_rise = True

                    self.current_sprite = 0

        

    def move(self):

        if not self.is_dead:
            if self.direction == -1:
                self.animate(self.walk_left_sprites, .5)
            else:
                self.animate(self.walk_right_sprites , .5)
            self.velocity += self.acceleration
            self.position += self.velocity + 0.5 * self.acceleration

            #update rect of the player image when he touches the boundary
            if self.position.x < 0:
                self.position.x = WINDOW_WIDTH
            elif self.position.x > WINDOW_WIDTH:
                self.position.x = 0
            
            self.rect.bottomleft = self.position

    def check_collisions(self):
        
        collided_platforms = pygame.sprite.spritecollide(self ,self.platform_group , False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0
        

        #portal collisons
        if pygame.sprite.spritecollide(self , self.portal_group , False):
            self.portal_sound.play()

            if self.position.x > WINDOW_WIDTH // 2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150

            if self.position.y > WINDOW_HEIGHT // 2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 134

    def check_animation(self):
        if self.animate_death:
            if self.direction == 1:
                self.animate(self.die_right_sprites , 0.95)
            else:
                self.animate(self.die_left_sprites , 0.95)
        
        if self.animate_rise:
            if self.direction == 1:
                self.animate(self.rise_right_sprites , .095)
            else:
                self.animate(self.rise_left_sprites , 0.95)

    def animate(self , sprites_list , speed):
        if self.current_sprite < len(sprites_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
            if self.animate_death:
                self.current_sprite = len(sprites_list) - 1
                self.animate_death = False
            
            #end rise animate
            if self.animate_rise:
                self.animate_rise = False
                self.is_dead = False
                self.frame_count = 0
                self.round_time = 0

        
        self.image = sprites_list[int(self.current_sprite)]

class RubyMaker(pygame.sprite.Sprite):
    def __init__(self , x, y , main_group):
        super().__init__()

        #animaton 
        self.ruby_sprites = []
        for i in range(7):
            self.ruby_sprites.append(pygame.transform.scale(pygame.image.load(f'images/ruby/tile00{i}.png') , (64 , 64)))

        #image and rect
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x , y)

        main_group.add(self)

    def update(self):
        self.animate(self.ruby_sprites , .2)

    def animate(self , sprites_list , speed):
        if self.current_sprite < len(sprites_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
        
        self.image = sprites_list[int(self.current_sprite)]


class Ruby(pygame.sprite.Sprite):
    def __init__(self , platform_group , portal_group):
        super().__init__()


        self.VERTICAL_ACCELERATION = 3
        self.HORIZONTAL_VELOCITY = 5

        self.ruby_sprites = []
        for i in range(7):
            self.ruby_sprites.append(pygame.transform.scale(pygame.image.load(f'images/ruby/tile00{i}.png') , (64 , 64)))

        #load images
        self.current_sprite = 0
        self.image = self.ruby_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (WINDOW_WIDTH //2 , 100)

        self.platform_group = platform_group
        self.portal_group = portal_group

        self.portal_sound = pygame.mixer.Sound('sounds/portal_sound.wav')

        self.position = vector(self.rect.x , self.rect.y)
        self.velocity = (random.randint(-1 * self.HORIZONTAL_VELOCITY , self.HORIZONTAL_VELOCITY) , 0)
        self.acceleration = vector(0 , self.VERTICAL_ACCELERATION)


    def update(self):
        self.move()
        self.check_collisions()
        self.animate(self.ruby_sprites , 0.25)

    def move(self):
        self.velocity += self.acceleration
        self.position += self.velocity + 0.5 * self.acceleration

        #update rect of the player image when he touches the boundary
        if self.position.x < 0:
            self.position.x = WINDOW_WIDTH
        elif self.position.x > WINDOW_WIDTH:
            self.position.x = 0
        self.rect.bottomleft = self.position

    def check_collisions(self):
        collided_platforms = pygame.sprite.spritecollide(self ,self.platform_group , False)
        if collided_platforms:
            self.position.y = collided_platforms[0].rect.top + 1
            self.velocity.y = 0
        

        #portal collisons
        if pygame.sprite.spritecollide(self , self.portal_group , False):
            self.portal_sound.play()

            if self.position.x > WINDOW_WIDTH // 2:
                self.position.x = 86
            else:
                self.position.x = WINDOW_WIDTH - 150

            if self.position.y > WINDOW_HEIGHT // 2:
                self.position.y = 64
            else:
                self.position.y = WINDOW_HEIGHT - 134


    def animate(self , sprites_list , speed):
        if self.current_sprite < len(sprites_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
        
        self.image = sprites_list[int(self.current_sprite)]

class Portal(pygame.sprite.Sprite):
    def __init__(self , x , y , color , portal_group):
        super().__init__()
        self.portal_sprites = []

        #portal animation
        if color == 'green':
            for i in range(21):
                if i < 10:
                    self.portal_sprites.append(pygame.transform.scale(pygame.image.load(f'images/portals/green/tile00{i}.png') , (72 , 72)))
                else:
                    self.portal_sprites.append(pygame.transform.scale(pygame.image.load(f'images/portals/green/tile0{i}.png') , (72 , 72)))
        else:
            for i in range(21):
                if i < 10:
                    self.portal_sprites.append(pygame.transform.scale(pygame.image.load(f'images/portals/purple/tile00{i}.png') , (72 , 72)))
                else:
                    self.portal_sprites.append(pygame.transform.scale(pygame.image.load(f'images/portals/purple/tile0{i}.png') , (72 , 72)))
        
        self.current_sprite = random.randint(0 , len(self.portal_sprites) - 1)
        self.image = self.portal_sprites[self.current_sprite]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x , y)

        portal_group.add(self)
    def update(self):
        self.animate(self.portal_sprites , .2)

    def animate(self , sprites_list , speed):
        if self.current_sprite < len(sprites_list) - 1:
            self.current_sprite += speed
        else:
            self.current_sprite = 0
        
        self.image = sprites_list[int(self.current_sprite)]
       
#create sprite groups
my_main_tile_group = pygame.sprite.Group()
my_platform_group =  pygame.sprite.Group()

my_player_group = pygame.sprite.Group()
my_bullet_group = pygame.sprite.Group()

my_zombie_group = pygame.sprite.Group()

my_portal_group = pygame.sprite.Group()
my_ruby_group = pygame.sprite.Group()

#0->no tile 1->dirt 2-5-> platforms , 6->ruby maker 7-8->portals  9->player
#23rows 40 column
tile_map = [
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [7,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,8,0],
    [4,4,4,4,4, 4,4,4,4,4, 4,4,4,4,5, 0,0,0,0,6, 0,0,0,0,0, 3,4,4,4,4, 4,4,4,4,4, 4,4,4,4,4],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,3,4,4,4, 4,4,4,4,4, 4,4,4,4,4, 4,4,4,5,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [4,4,4,4,4, 5,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,3, 4,4,4,4,4],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [4,4,4,4,4, 4,4,4,4,4, 4,4,4,4,4, 5,0,0,0,0, 0,0,0,0,3, 4,4,4,4,4, 4,4,4,4,4, 4,4,4,4,4],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 9,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,3,4, 4,5,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0],
    [8,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,0,0, 0,0,0,7,0],
    [2,2,2,2,2, 2,2,2,2,2, 2,2,2,2,2, 2,2,2,2,2, 2,2,2,2,2, 2,2,2,2,2, 2,2,2,2,2, 2,2,2,2,2],
    [1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1, 1,1,1,1,1]
]


#generate tile objects 
for i in range(len(tile_map)):
    for j in range(len(tile_map[i])):
        #dirt tile
        if tile_map[i][j] == 1:
            Tile(j * 32 , i * 32 , 1 , my_main_tile_group)
        #platform tile
        elif tile_map[i][j] == 2:
            Tile(j*32 , i *32 , 2 , my_main_tile_group , my_platform_group)
        elif tile_map[i][j] == 3:
            Tile(j*32 , i * 32 , 3 , my_main_tile_group , my_platform_group)
        elif tile_map[i][j] == 4:
            Tile(j*32 , i * 32 , 4 , my_main_tile_group , my_platform_group)
        elif tile_map[i][j] == 5:
            Tile(j*32 , i * 32 , 4 , my_main_tile_group , my_platform_group)
        #Ruby maker
        elif tile_map[i][j] == 6:
            RubyMaker(j * 32 , i * 32 , my_main_tile_group)
        #portals
        elif tile_map[i][j] == 7:
            Portal(j * 32 , i * 32 , "green" , my_portal_group)
        elif tile_map[i][j] == 8:
            Portal(j*32 , i * 32 , "purple" , my_portal_group)
        #player
        elif tile_map[i][j] == 9:
            my_player  = Player(j*32 - 32, i*32 + 32 , my_platform_group , my_portal_group , my_bullet_group)
            my_player_group.add(my_player)
        


#load background image
background_image = pygame.transform.scale(pygame.image.load("images/background.png") , (WINDOW_WIDTH , WINDOW_HEIGHT))
background_rect = background_image.get_rect()
background_rect.topleft = (0, 0)

#creat game object
my_game = Game(my_player , my_zombie_group, my_platform_group , my_portal_group , my_bullet_group , my_ruby_group)
my_game.pause_game("Zombie Knight" , "press enter to begin")
pygame.mixer.music.play(-1 , 0.0)
#game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                my_player.jump()
            if event.key == pygame.K_k:
                my_player.fire()

    #draw background
    display_surface.blit(background_image , background_rect)

    #draw tiles
    my_main_tile_group.update()
    my_main_tile_group.draw(display_surface)


    #draw and update portal group
    my_portal_group.update()
    my_portal_group.draw(display_surface)

    #update and draw game
    my_game.update()
    my_game.draw()

    #player group 
    my_player_group.update()
    my_player_group.draw(display_surface)

    #bullet group
    my_bullet_group.update()
    my_bullet_group.draw(display_surface)

    #update zombie
    my_zombie_group.update()
    my_zombie_group.draw(display_surface)

    #ruby group
    my_ruby_group.update()
    my_ruby_group.draw(display_surface)

    pygame.display.update()
    clock.tick(FPS)


#quit
pygame.quit()