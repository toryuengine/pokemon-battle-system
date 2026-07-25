#pragma once
#include <vector>
#include <iostream>


class ChooseCharacter {
    public:
        std::vector<int> select();
        

    private:
    std::vector<std::string> charalist=
    {
        "バクフーン", 
        "ラグラージ", 
        "フシギバナ",
        "リザードン",
        "エンペルト",
        "ジュカイン",
    };

    //選択中のカーソルを出力する
    int getCursor(); 

    //描画する
    void writeConsole(int select, std::vector <std::string> list);

    //ボタンに応じてポジションの位置を変更する
    int changePosition(int position, int selectbtn, int range);
        
    //三体選択した時に、本当にこのポケモンでいいかの確認
    bool askToConfirm(std::vector<int> chooselist);

    bool askYesNo();
};