#include <iostream>
#include <cstdlib> // std::system のために必要
#include <string>
#include <vector>
struct Status {
    int lv;
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};

//種族値
struct Racial {
    int lv;
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};

//個体値
struct individual {
    int lv;
    int hp;
    int attack;
    int defense;
    int sp_attack;
    int sp_defence;
    int speed;
};

class Basic_status_calc {
    private:
        Racial Typhlosion = {50, 78, 84, 78, 109, 85, 100};
        Racial Swampert = {50, 100, 110, 90, 85, 90, 60};
        
        Status status;

    public:
        int name;
        Racial getPokemon1() const {
            return Typhlosion;
        }

        //種族値をセットする
        void setRacial(const Racial arg) {
            Racial racial = arg;
            setStatus(racial);
        };

        void setStatus(Racial arg) {
            status.hp = calcStatus(arg.lv, arg.hp);
            status.attack = calcStatus(arg.lv, arg.attack);
            status.defense = calcStatus(arg.lv, arg.defense);
            status.sp_attack = calcStatus(arg.lv, arg.sp_attack);
            status.sp_defence = calcStatus(arg.lv, arg.sp_defence);
            status.speed = calcStatus(arg.lv, arg.speed);
        };

        //ステータスを算出する
        int calcStatus(int lv, int status) {
            int calkEffort = 252 / 4;
            int calk1 = status * 2 + 31 + calkEffort;
            int calk2 = calk1 * lv;
            int calk3 = calk2 / 100;
            int finalStatus = calk3 + 5;

            return finalStatus;
        };

        Status getStatus() {
            return status;
        };
};


int main() {
    Basic_status_calc basic;
    Racial me = basic.getPokemon1();
    basic.setRacial(me);
    Status status = basic.getStatus();
    
    std::cout << status.hp << std::endl;
    std::cout << status.attack << std::endl;
    std::cout << status.defense << std::endl;
    std::cout << status.sp_attack << std::endl;
    std::cout << status.sp_defence << std::endl;
    std::cout << status.speed << std::endl;
    return 0;


    // int i = 1;
    // Status Typhlosion = {220, 15}; //ラグラージ
    // Status Swampert = {204, 22};//バクフーン
    // std::system("chcp 65001"); // コンソールをUTF-8モードに変更
    // bool battle = true;

    // while (battle) {
    //     std::cout << "ターン" << i << std::endl;

    //     // if-else文を使うことで、条件分岐を1回にまとめる
    //     // if (i % 2 != 0) {
            
    //     Swampert.hp = Swampert.hp - Typhlosion.attack;
    //     std::cout << "ラグラージの残りＨＰ" << Swampert.hp << std::endl;

    //     // } else {
    //     Typhlosion.hp = Typhlosion.hp - Swampert.attack;
    //     std::cout << "バクフーンの残りＨＰ" << Typhlosion.hp << std::endl;
    //     // }

    //     std::cin.get(); 
    //     i++;

    // //戦闘終了
    //     if(Typhlosion.hp <= 0) {
    //         battle = false;
    //     }else if (Swampert.hp <= 0) {
    //         battle = false;
    //     }
    // }
    // std::cout << "戦闘終了" << std::endl;
    // return 0; // 無限ループのため実際には到達しません
};
