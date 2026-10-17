# Reinforcement Learning from Human Feedback

Reinforcement learning from human feedback, or RLHF, aligns a language model's behavior
with human preferences. It addresses a fundamental problem: the qualities we want in a
response, such as helpfulness, honesty, and harmlessness, are hard to specify as a
differentiable loss, but humans can compare two responses and say which is better.

RLHF proceeds in three stages. First, supervised fine-tuning teaches the model to follow
instructions using demonstration data. Second, a reward model is trained on human
comparisons: given two responses to the same prompt, it learns to predict which one
humans prefer, turning pairwise preferences into a scalar score. Third, the language
model is optimized against the reward model using a reinforcement learning algorithm,
most classically proximal policy optimization, while a penalty on divergence from the
original model keeps it from drifting too far and gaming the reward.

The reward model is the heart of the method, and also its main vulnerability. Because the
policy is optimized to maximize the reward, it can learn to exploit weaknesses in the
reward model, producing outputs that score highly without being genuinely better. This
phenomenon, called reward hacking or over-optimization, is why the divergence penalty and
careful reward-model validation are essential.

RLHF is powerful but complex and notoriously unstable, sensitive to hyperparameters and
reward-model quality. Direct Preference Optimization simplifies the process by fitting
human preferences directly with a supervised objective, removing the separate reward
model and the reinforcement learning loop. This and related methods have become popular
for aligning modern models, but the underlying goal remains the same: converting the
non-differentiable notion of human preference into a signal that training can follow.
An alternative and increasingly common approach replaces the reinforcement learning stage
with a direct objective on preference pairs. Rather than training a separate reward model
and then optimizing a policy against it, methods such as direct preference optimization
reformulate the problem so that the language model itself can be trained on pairs of
preferred and dispreferred responses with a supervised-style loss. This removes an entire
component and much of the instability, while retaining most of the benefit. The trade-off is
less flexibility than a full reinforcement learning setup, but for alignment at typical
scales the simpler methods are often the pragmatic choice, and they illustrate a recurring
pattern in machine learning where a clever reformulation replaces a complicated system.
