# import bibliotecas
import pygame, random, os
from spritesheet import SpriteSheet
from enemy import Enemy
from pygame import mixer

# iniciar pygame
mixer.init()
pygame.init()

#dimensoes da janela do jogo
tela_largura = 400
tela_altura = 600

#criando a janela do jogo
tela = pygame.display.set_mode((tela_largura, tela_altura))
pygame.display.set_caption('Naruto Jump')

#definindo o fps
clock = pygame.time.Clock()
FPS = 60

#carregar musica e sons
pygame.mixer.music.load('sons/videoplayback.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0)
jump_fx = pygame.mixer.Sound('sons/jump.mp3')
jump_fx.set_volume(0.5)
death_fx = pygame.mixer.Sound('sons/death.mp3')
death_fx.set_volume(0.5)

#variaveis do jogo
scroll_thresh = 200
gravidade = 1
max_plataformas = 10
scroll = 0
bg_scroll = 0
game_over = False
score = 0
fade_counter = 0

if os.path.exists('score.txt'):
    with open('score.txt', 'r') as file:
        high_score = int(file.read())
else:
    high_score = 0

#definindo cores
branco = (255, 255, 255)
vermelho = (255, 0, 0)
preto = (0, 0, 0)
painel = (153, 217, 234)

#definindo fontes
fonte_pequena = pygame.font.SysFont('Lucida Sans', 20)
fonte_grande = pygame.font.SysFont('Lucida Sans', 24)

# carregando imagens
bg_image = pygame.image.load('images/bg.png').convert_alpha()
jump_image = pygame.image.load('images/jump.gif').convert_alpha()
plataforma_image = pygame.image.load('images/wood.png').convert_alpha()
#shuriken sprite
bird_sheet_img = pygame.image.load('images/bird.png').convert_alpha()
bird_sheet = SpriteSheet(bird_sheet_img)

#funcçao para colocar texto na tela
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    tela.blit(img, (x, y))


#função para desenhar um painel de informaçoes
def draw_painel():
    pygame.draw.rect(tela, painel, (0, 0, tela_largura, 30))
    draw_text('PONTUAÇÃO: ' + str(score), fonte_pequena, branco, 0, 0)


#função para desenhar o background
def draw_bg(bg_scroll):
    tela.blit(bg_image, (0, 0 + bg_scroll))
    tela.blit(bg_image, (0, -600 + bg_scroll))


#classe do player
class Player():
    def __init__(self, x, y):
        self.image = pygame.transform.scale(jump_image, (45, 45))
        self.largura = 25
        self.altura = 40
        self.rect = pygame.Rect(0, 0, self.largura, self.altura)
        self.rect.center = (x, y)
        self.vel_y = 0
        self.flip = False

    def move(self):
        #resetando variaveis
        scroll = 0
        dx = 0
        dy = 0

        #processo de pressionar teclas
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT]:
            dx = -10
            self.flip = True
        if key[pygame.K_RIGHT]:
            dx = 10
            self.flip = False

        #gravidade
        self.vel_y += gravidade
        dy += self.vel_y

        #assegurando que o jogador nao saia da tela
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx >tela_largura:
            dx = tela_largura - self.rect.right


        #check colisão com plataformas
        for plataforma in plataforma_grupo:
            #colisão na direçao y
            if plataforma.rect.colliderect(self.rect.x, self.rect.y + dy, self.largura, self.altura):
                #check se esta abaixo da plataforma
                if self.rect.bottom < plataforma.rect.centery:
                    if self.vel_y > 0:
                        self.rect.bottom = plataforma.rect.top
                        dy = 0
                        self.vel_y = -19
                        jump_fx.play()

        #check se o jogador passou do topo da tela
        if self.rect.top <= scroll_thresh:
            if self.vel_y <0:
                scroll = -dy

        #atualizando a posição do retangulo
        self.rect.x += dx
        self.rect.y += dy + scroll

        #atualizar a mascara
        self.mask = pygame.mask.from_surface(self.image)

        return scroll

    def draw(self):
        tela.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - 10, self.rect.y - 3 ))

class Plataforma(pygame.sprite.Sprite):
    def __init__(self, x, y, largura, moving):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(plataforma_image, (largura, 10))
        self.moving = moving
        self.move_counter = random.randint(0, 50)
        self.direction = random.choice([-1, 1])
        self.speed = random.randint(1, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll):
        #mover a plataformando de um lado para o outro
        if self.moving == True:
            self.move_counter +=1
            self.rect.x += self.direction * self.speed

        #mudar a plataforma de direção se bater numa parede
        if self.move_counter >= 100 or self.rect.left < 0 or self.rect.right > tela_largura:
            self.direction *= -1
            self.move_counter = 0


        #update de plataformas na posição vertical
        self.rect.y += scroll

        #check se as plataformas sairam da tela
        if self.rect.top > tela_altura:
            self.kill()


#instancia do player
jump = Player(tela_largura // 2, tela_altura -150)

#criando grupos de sprite
plataforma_grupo = pygame.sprite.Group()
enemy_grupo = pygame.sprite.Group()

#criando plataformas iniciais
plataforma = Plataforma(tela_largura // 2 - 50 , tela_altura - 50, 100, False)
plataforma_grupo.add(plataforma)

#loop do jogo
run = True
while run:

    clock.tick(FPS)

    if game_over == False:

        scroll = jump.move()

        #desenhando o background
        bg_scroll += scroll
        if bg_scroll >= 600:
            bg_scroll = 0
        draw_bg(bg_scroll)

        #gerando plataformas
        if len(plataforma_grupo)  < max_plataformas:
            p_w = random.randint(35, 70)
            p_x = random.randint(0, tela_largura - p_w)
            p_y = plataforma.rect.y - random.randint(80, 120)
            p_type = random.randint(1, 2)
            if p_type == 1 and score > 1000:
                p_moving = True
            else:
                p_moving = False
            plataforma = Plataforma(p_x, p_y, p_w, p_moving)
            plataforma_grupo.add(plataforma)

        #atualizando plataformas
        plataforma_grupo.update(scroll)

        #gerando inimigos
        if len(enemy_grupo) == 0 and score > 1500:
            enemy = Enemy(tela_largura, 100, bird_sheet, 1.5)
            enemy_grupo.add(enemy)


        #atualizando inimigos

        enemy_grupo.update(scroll, tela_largura)
        #atualizando pontuação
        if scroll > 0:
            score += scroll

        #desenhar algo para quando ultrapassar o high score
        pygame.draw.line(tela, branco, (0, score - high_score + scroll_thresh), (tela_largura, score - high_score + scroll_thresh), 3)
        draw_text('PONTUAÇÃO RECORDE', fonte_pequena, branco, tela_largura - 230, score - high_score + scroll_thresh)


        #desenhando sprites
        plataforma_grupo.draw(tela)
        enemy_grupo.draw(tela)
        jump.draw()

        #desenhando painel
        draw_painel()


        #check game over
        if jump.rect.top > tela_altura:
            game_over = True
            death_fx.play()
        #check colisão com inimigos
        if pygame.sprite.spritecollide(jump, enemy_grupo, False):
            if pygame.sprite.spritecollide(jump, enemy_grupo, False, pygame.sprite.collide_mask):
                game_over = True
                death_fx.play()

    else:
         if fade_counter < tela_largura:
             fade_counter += 5
             for y in range(0, 6, 2):
                pygame.draw.rect(tela, preto, (0, y * 100, fade_counter, 100))
                pygame.draw.rect(tela, preto, (tela_largura - fade_counter, (y+1) * 100, tela_largura, 100))
         else:
             draw_text('GAME OVER', fonte_grande, branco, 90, 200)
             draw_text('PONTUAÇÃO: ' + str(score), fonte_grande, branco, 90, 250)
             draw_text('PRESSIONE', fonte_grande, branco, 90, 300)
             draw_text('ESPAÇO', fonte_grande, vermelho, 220, 300)
             draw_text('PARA JOGAR NOVAMENTE', fonte_grande, branco, 40, 350)
             #atualizando o high score
             if score> high_score:
                 high_score = score
                 with open('score.txt', 'w') as file:
                     file.write(str(high_score))
             key = pygame.key.get_pressed()
             if key[pygame.K_SPACE]:
                #RESETAR VARIAVEIS
                game_over = False
                score = 0
                scroll = 0
                fade_counter = 0
                #reposicionar o ninja
                jump.rect.center = (tela_largura // 2, tela_altura - 150)
                #resetar inimigos
                enemy_grupo.empty()
                #reiniciar plataformas
                plataforma_grupo.empty()
                # criando plataformas iniciais
                plataforma = Plataforma(tela_largura // 2 - 50, tela_altura - 50, 100, False)
                plataforma_grupo.add(plataforma)

    #manipulador de evento
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if score > high_score:
                high_score = score
                with open('score.txt', 'w') as file:
                    file.write(str(high_score))
            run = False


    #atualizando a janela
    pygame.display.update()



pygame.quit()
