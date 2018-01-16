from pandaeditor import *

class Skill():

    def __init__(self):
        self.targets = list()

        self.target_type = 'self, friend, single, multiple, all'
        self.damage = 0
        self.damage_type = 'physical'
        self.bleed_damage = 0


    def cast(self):

        for t in self.targets:
            t.health -= self.damage



player.cast_spell(Fireball(target=mouse.hovered_entity))

book_0.skill = skills.Fireball()
if self.skill.require_target:
    pass
else:
    self.skill.cast()


class Fireball(Skill):

    def __init__(self, target):
        super().__init__(self, target)
        self.name = 'Fireball'
        self.target_type = 'single'
        self.damage = 20 * player.int
        self.damage_type = 'fire'

        self.dot_damage = 5
        self.turns_left = 3

        self.mana_cost = 10
        # self.health_cost = 10%

        self.description = '''
            If target has more than 50% hp, burn the enemy for 5 * INT fire damage for 3 turns.
            Else, deal 100 damage.
            Unfreezes target.
            Costs 10 mana.
            '''
            
    def cast(self):
        if target.hp > target.hp / 2:
            target.hp -= self.damage
        else:
            player.inflict_burn(target, self.dot_damage)

        if 'frozen' in target.debuffs:
            target.debuffs.remove('frozen')

        if self.dot:
            target.dots.append(self)

    def eval_dot(self):
        self.turns -= 1
        if self.turns <= 0:
            self.end()

    def end(self):
        print('burning ended')
