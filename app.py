import uvicorn
from fastapi import FastAPI
from collections import defaultdict
from contextlib import asynccontextmanager
from typing import Optional
from samplers import UCBSampler, ThompsonSampler

# Dictionary to store recommendations for each click ID
recommendations = {}

# Counter for the number of clicks each offer receives
offer_clicks = defaultdict(int)

# Counter for the number of actions (conversions) for each offer
offer_actions = defaultdict(int)

# Cumulative rewards for each offer
offer_rewards = defaultdict(float)


def reset_stats():
    """
    Reset all statistics and clear data structures.

    This function clears the following global dictionaries:
    - recommendations: Stores click_id to offer_id mappings
    - offer_clicks: Counts clicks for each offer
    - offer_actions: Counts conversions for each offer
    - offer_rewards: Sums rewards for each offer
    """
    recommendations.clear()
    offer_clicks.clear()
    offer_actions.clear()
    offer_rewards.clear()


# For newer versions of FastAPI:

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Clear statistics"""
    reset_stats()
    yield


app = FastAPI(lifespan=lifespan)


# For older versions of FastAPI:

# app = FastAPI()


# @app.on_event("startup")
# def startup() -> None:
#     """
#     Initialize statistics when the application starts.

#     This function is called automatically when the FastAPI application starts.
#     It clears all global dictionaries to ensure a clean state at startup.
#     """
#     recommendations.clear()
#     offer_clicks.clear()
#     offer_actions.clear()
#     offer_rewards.clear()


@app.put("/feedback/")
def feedback(click_id: int, reward: float) -> dict:
    """
    Process feedback for a particular click and update statistics.

    Args:
        click_id (int): The unique identifier for the click.
        reward (float): The reward value associated with the click.

    Returns:
        dict: A dictionary containing feedback information:
            - click_id: The ID of the processed click
            - offer_id: The ID of the offer associated with the click
            - is_conversion: Boolean indicating
            whether the click resulted in a conversion
            - reward: The reward value received

    This function updates offer statistics based on the feedback received:
    - Removes the click_id from recommendations
    - Updates offer_rewards and offer_actions if a conversion occurred
    """
    offer_id = recommendations[click_id]
    del recommendations[click_id]

    if reward > 0:
        offer_rewards[offer_id] += reward
        offer_actions[offer_id] += 1
        is_conversion = True
    else:
        is_conversion = False

    response = {
        "click_id": click_id,
        "offer_id": offer_id,
        "is_conversion": is_conversion,
        "reward": reward,
    }

    return response


@app.get("/offer_ids/{offer_id}/stats/")
def stats(offer_id: int) -> dict:
    """
    Retrieve statistics for a specific offer.

    Args:
        offer_id (int): The unique identifier of the offer.

    Returns:
        dict: A dictionary containing the following statistics for the offer:
            - offer_id: The ID of the offer
            - clicks: Total number of clicks for the offer
            - conversions: Total number of conversions for the offer
            - reward: Total reward accumulated for the offer
            - cr: Conversion rate (conversions / clicks)
            - rpc: Revenue per click (total reward / clicks)

    This function calculates and returns
    various performance metrics (stats) for the specified offer.
    """
    response = {
        "offer_id": offer_id,
        "clicks": offer_clicks[offer_id],
        "conversions": offer_actions[offer_id],
        "reward": offer_rewards[offer_id],
        "cr": offer_actions[offer_id] / max(offer_clicks[offer_id], 1),
        "rpc": offer_rewards[offer_id] / max(offer_clicks[offer_id], 1),
    }
    return response


@app.get("/sample/")
def sample(
    click_id: int,
    offer_ids: str,
    sampler: Optional[str] = "ucb",
    ucb_c: Optional[float] = 1.0,
    thompson_a: Optional[float] = 1.0,
    thompson_b: Optional[float] = 1.0
) -> dict:
    """
    Sample a random offer using the specified sampling strategy.

    Args:
        click_id (int): The unique identifier for the current click.
        offer_ids (str): A comma-separated string of offer IDs to choose from.
        sampler (str, optional): The sampling strategy to use.
        Either "ucb" or "thompson". Defaults to "ucb".
        ucb_c (float, optional): The exploration parameter for UCB sampling.
        Defaults to 1.0.
        thompson_a (float, optional): Hyperparameter for alpha
        in Thompson sampling. Defaults to 1.0.
        thompson_b (float, optional): Hyperparameter for beta
        in Thompson sampling. Defaults to 1.0.

    Returns:
        dict: A dictionary containing:
            - click_id: The ID of the current click
            - offer_id: The ID of the sampled offer

    Raises:
        ValueError: If an unknown sampler is specified.

    This function selects an offer using either UCB or Thompson sampling,
    updates the recommendations and offer_clicks dictionaries,
    and returns the sampled offer ID.
    """
    offers_ids = [int(offer) for offer in offer_ids.split(",")]

    if sampler == "ucb":
        ucb_sampler = UCBSampler(
            ucb_c, offer_clicks, offer_actions, offer_rewards
        )
        offer_id = ucb_sampler.sample(offers_ids, click_id)
    elif sampler == "thompson":
        thompson_sampler = ThompsonSampler(
            thompson_a, thompson_b, offer_clicks, offer_actions, offer_rewards
        )
        offer_id = thompson_sampler.sample(offers_ids)
    else:
        raise ValueError(f"Unknown sampler: {sampler}")

    recommendations[click_id] = offer_id
    offer_clicks[offer_id] += 1

    response = {
        "click_id": click_id,
        "offer_id": offer_id
    }

    return response


def main() -> None:
    """
    Run the FastAPI application using uvicorn.

    This function starts the FastAPI server using uvicorn,
    hosting the application on localhost.
    """
    uvicorn.run("app:app", host="localhost")


if __name__ == "__main__":
    main()
