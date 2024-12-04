import pyterm

if __name__ == "__main__":
    window = pyterm.Display((500, 100), pyterm.FULLSCREEN)
    image = pyterm.image.Image((20, 20))
    image.fill((255, 255, 255))
    rect = image.to_rect(topleft=(0, 0))
    dx, dy = 1, 1

    clock = pyterm.Clock()

    try:
        while True:
            window.fill(None)

            pyterm.draw.rect(window, (255, 255, 255), (0, 0, window.width, window.height), 1)

            if rect.x < 0 or rect.x + rect.width >= window.width:
                dx *= -1
            if rect.y < 0 or rect.y + rect.height >= window.height:
                dy *= -1

            rect.topleft = (rect.topleft[0] + dx, rect.topleft[1] + dy)

            window.blit(image, rect.topleft)
            window.update()
            clock.tick(60)
    except KeyboardInterrupt:
        window.exit()

