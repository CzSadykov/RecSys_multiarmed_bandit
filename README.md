# Multi-Armed Bandits Microservice for CPA Platform

This project implements a simple system for optimizing offer selection in a Cost-Per-Action (CPA) platform using sampling strategies from Reinforcement Learning (UCB and Thompson Sampling).

## Overview

This  microservice is an example of an intelligent intermediary between advertisers and traffic arbitrageurs in a CPA platform. Our system focuses on maximizing rewards by paying arbitrageurs for actual conversions (desired actions) such as purchases, subscriptions, registrations, etc., as defined by advertisers when creating offers on our platform.

Sampling with the Upper Confidence Bound (UCB) or Thompson Sampling methods (depending on your choice) allows you to balance exploration and exploitation, ensuring that system learns from user interactions while maximizing overall performance and revenue.

Of course real-world microservices are more complex and should include more sophisticated algorithms for offer selection and ranking, as well as more sophisticated data storage and processing techniques. But this minimalistic version should give you a good understanding of the concept and the code should be easy to extend and modify.

## Key Components

### 1. App (app.py)

The `app.py` file contains the FastAPI application that serves as the backbone of our microservice. Here's what it offers:

- **Endpoints**:
  - `/feedback/`: Processes conversion data for a given click
  - `/offer_ids/{offer_id}/stats/`: Retrieves performance statistics for a specific offer
  - `/sample/`: Intelligently samples an offer using the specified strategy

- **Data Management**:
  - Maintains dictionaries for recommendations, offer clicks, actions (conversions), and rewards
  - Provides a `reset_stats()` function to clear all data structures


### 2. Samplers (samplers.py)

The `samplers.py` file implements our Reinforcement Learning sampling strategies:

#### UCB Sampler

The UCB (Upper Confidence Bound) strategy balances exploration and exploitation by selecting offers based on their estimated upper bound of performance.

Key features:
- Calculates UCB for each offer using click and reward data
- Adjustable exploration parameter (`ucb_c`)
- Combines conversion rate (CR) and revenue per click (RPC) for optimal selection

#### Thompson Sampler

Thompson Sampling uses a Bayesian approach, modeling the uncertainty of each offer's performance and sampling from the posterior distribution.

Key features:
- Uses Beta distribution to model offer performance
- Adjustable prior parameters (`thompson_a` and `thompson_b`)
- Combines conversion rate (CR) and revenue per click (RPC) for decision making

## How It Works

1. When a request comes in, the `/sample/` endpoint is called with a list of eligible offer IDs and sampling parameters.
2. The chosen sampler (UCB or Thompson) selects an offer based on current performance statistics and sampling strategy.
3. The selected offer is presented to the user via the traffic arbitrageur's channel.
4. Conversion data is collected via the `/feedback/` endpoint, updating offer statistics.
5. Over time, the system learns which offers perform best for different traffic sources and adjusts its selections accordingly, maximizing overall platform revenue.

## Getting Started

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the FastAPI application:
   ```
   uvicorn app:app --reload
   ```

3. Use the provided endpoints to integrate the microservice with your CPA platform and optimize your offer selection process!

## Conclusion

This Multi-Armed Bandits Microservice provides a powerful tool for optimizing offer selection in real-time within a CPA platform. By leveraging advanced Reinforcement Learning strategies... I'm surprised you're still reading this lol. Have a great rest of your day. Cheers!
