import numpy as np


class UCBSampler:
    def __init__(
            self,
            ucb_c: float = 1.0,
            offer_clicks: dict = None,
            offer_actions: dict = None,
            offer_rewards: dict = None
    ):
        self.ucb_c = ucb_c
        self.offer_clicks = offer_clicks
        self.offer_actions = offer_actions
        self.offer_rewards = offer_rewards

    def sample(self, offers_ids: list, click_id: int) -> int:
        rpc_ucb = {}
        for offer in offers_ids:
            clicks = self.offer_clicks.get(offer, 0)
            reward = self.offer_rewards.get(offer, 0)
            cr = self.offer_actions[offer] / max(clicks, 1)
            rpc = reward / max(clicks, 1)
            ucb = cr + self.ucb_c * np.sqrt(
                np.log1p(click_id)) / max(clicks, 1
                                          )
            rpc_ucb[offer] = rpc * ucb
        return max(rpc_ucb, key=rpc_ucb.get)


class ThompsonSampler:
    def __init__(
            self,
            thompson_a: float = 1.0,
            thompson_b: float = 1.0,
            offer_clicks: dict = None,
            offer_actions: dict = None,
            offer_rewards: dict = None
    ):
        self.thompson_a = thompson_a
        self.thompson_b = thompson_b
        self.offer_clicks = offer_clicks
        self.offer_actions = offer_actions
        self.offer_rewards = offer_rewards

    def sample(self, offers_ids: list) -> int:
        alpha = np.array(
            [self.offer_actions[offer] for offer in offers_ids])  # successes
        beta = np.array(
            [self.offer_clicks[offer] - self.offer_actions[offer]
             for offer in offers_ids]
            )  # failures

        if sum(alpha) == 0:
            return int(np.random.choice(offers_ids))
        else:
            cr = np.random.beta(
                alpha + self.thompson_a, beta + self.thompson_b
            )
            rpc = np.array(
                [self.offer_rewards[offer] / max(self.offer_clicks[offer], 1)
                 for offer in offers_ids]
            )
            return offers_ids[np.argmax(cr * rpc)]
