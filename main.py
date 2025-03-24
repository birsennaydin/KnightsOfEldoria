from controllers.simulation_controller import SimulationController
from utils.enums import HunterSkill, TreasureType


def main():
    print("⚔️ Knights of Eldoria Simulation Started ⚔️")

    controller = SimulationController(grid_size=10)

    # Add a hideout
    controller.add_hideout(0, 0)

    # Add a hunter
    controller.add_hunter("Ela", HunterSkill.NAVIGATION, 1, 1)

    # Add a knight
    controller.add_knight("Yavuz", 5, 5)

    # Add some treasures
    controller.add_treasure(2, 2, TreasureType.GOLD)
    controller.add_treasure(3, 3, TreasureType.SILVER)
    controller.add_treasure(4, 4, TreasureType.BRONZE)

    # Run simulation
    controller.run(steps=50)

    # NLP demo: make Ela express some thoughts
    print("\n🗣️ Sentiment Analysis Demo:")
    for hunter in controller.hunters:
        if hunter.name == "Ela":
            hunter.express_opinion("I love finding treasure and helping my team.")
            hunter.express_opinion("I'm exhausted and scared of the knights.")
            hunter.express_opinion("Today is just okay.")

    print("✅ Simulation Ended")


if __name__ == "__main__":
    main()
