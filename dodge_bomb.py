import os
import sys
import pygame as pg
import random
import time

WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:(0,-5),
    pg.K_DOWN:(0,+5),
    pg.K_LEFT:(-5,0),
    pg.K_RIGHT:(+5,0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct:pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectか爆弾Rect
    戻り値：タプル（横方向判定結果、縦方向結果）
    画面内ならTrue、画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:  # 横方向のはみ出しのチェック
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向のはみ出しのチェック
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    引数：screeのSurface
    戻り値：なし
    ゲームオーバー画面の表示
    """
    go_img = pg.Surface((1100, 650))
    pg.draw.rect(go_img, (0, 0, 0), (0, 0, 1100, 650))
    go_img.set_alpha(255)
    fonto = pg.font.Font(None, 80)
    go_txt = fonto.render("Game Over", True, (255, 255, 255))
    go_img.blit(go_txt,[400,300])
    kkgo_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    go_img.blit(kkgo_img,[350, 300])
    go_img.blit(kkgo_img,[710, 300])
    screen.blit(go_img,[0,0])
    pg.display.update()
    time.sleep(5)


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    引数：なし
    戻り値：移動量タプルと対応する画像Surface
    """
    kk_img1 = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_img2 = pg.transform.flip(kk_img1, True, False)
    kk_dict = {
        (0, 0): pg.transform.rotozoom(kk_img2, 0, 1.0),  # 右から反時計回りに8方向の画像
        (+5, 0): pg.transform.rotozoom(kk_img2, 0, 1.0),
        (+5, -5): pg.transform.rotozoom(kk_img2, 45, 1.0),
        (0, -5): pg.transform.rotozoom(kk_img2, 90, 1.0),
        (-5, -5): pg.transform.rotozoom(kk_img1, 325, 1.0),
        (-5, 0): pg.transform.rotozoom(kk_img1, 360, 1.0),
        (-5, +5): pg.transform.rotozoom(kk_img1, 45, 1.0),
        (0, +5): pg.transform.rotozoom(kk_img2, 270, 1.0),
        (+5, +5): pg.transform.rotozoom(kk_img2, 325, 1.0), 
    }
    return kk_dict


def init_bb_img() -> tuple[list[pg.Surface], list[int]]:
    """
    引数：なし
    戻り値：大きさを変えた爆弾Surfaceのリストと加速度のリスト
    """
    bb_imgs = []
    bb_accs = [a for a in range(1, 11)]
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)
        bb_img.set_colorkey((0, 0, 0)) 
        bb_imgs.append(bb_img)  # 10段階の大きさの爆弾のリスト
    
    return bb_imgs, bb_accs


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    引数：爆弾とこうかとんRect,爆弾の移動方向のタプル
    戻り値：新しい爆弾の移動方向のタプル
    こうかとんにむかって追尾するようになる
    """
    def_x = org.x - dst.x  # 横方向の差を求める
    def_y = org.y - dst.y  # 縦方向の差を求める
    length = (def_x ** 2 + def_y ** 2) ** 0.5  # 以上の式から双方の距離を求める
    regular = 50 ** 0.5  
    if length < 300.0:  # 距離が300未満ならもとの方向に移動
        return current_xy
    new_x = def_x / length  * regular  # 正規化後の横方向のベクトル
    new_y = def_y / length  * regular  # 正規化後の縦方向のベクトル
    return (new_x, new_y)


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20))  # 空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10,  10), 10)  # 半径10の赤い円を描画
    bb_img.set_colorkey((0, 0, 0))  
    bb_rct = bb_img.get_rect()  # 爆弾Rect
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
    vx, vy = +5, +5  # 爆弾の横速度, 縦速度
    clock = pg.time.Clock()
    tmr = 0
    bb_imgs, bb_accs = init_bb_img()  # 爆弾の画像と速さのリストを取得
    kk_imgs = get_kk_imgs()  # こうかとん画像の取得
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            
        if kk_rct.colliderect(bb_rct):  # こうかとんと爆弾が衝突したら
            print("ゲームオーバー")
            gameover(screen)
            return
        
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        
        sum_mv = [0,0]
        # if key_lst[pg.K_UP]:
        #     sum_mv[1] -= 5
        # if key_lst[pg.K_DOWN]:
        #     sum_mv[1] += 5
        # if key_lst[pg.K_LEFT]:
        #     sum_mv[0] -= 5
        # if key_lst[pg.K_RIGHT]:
        #     sum_mv[0] += 5
        for key , mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]  # 横方向の移動量
                sum_mv[1] += mv[1]  # 縦方向の移動量
        kk_img = kk_imgs[tuple(sum_mv)]
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])
        screen.blit(kk_img, kk_rct)

        
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向にはみ出ていたら
            vx *= -1
        if not tate:  # 縦方向にはみ出ていたら
            vy *= -1
            
        avx = vx*bb_accs[min(tmr//500, 9)]  #10秒ごとに1段階ずつ横方向に早くなる
        avy = vy*bb_accs[min(tmr//500, 9)]  #10秒ごとに1段階ずつ縦方向に早くなる
        bb_img = bb_imgs[min(tmr//500, 9)]  #10秒ごとに爆弾が大きくなる
        #avx, avy = calc_orientation(bb_rct, kk_rct,(avx,avy))
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height
        bb_rct.move_ip(avx, avy)
        screen.blit(bb_img, bb_rct)
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
