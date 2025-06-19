from trivoting.election.generate import generate_random_profile

from prefsampling.approval import urn, resampling, noise

def get_random_profile(num_alt, num_ballots):
    return generate_random_profile(
        num_alt,
        num_ballots,
        lambda num_voters, num_candidates: urn(num_voters, num_candidates, p=0.5, alpha=0.7),
        lambda num_voters, num_candidates: resampling(num_voters, num_candidates, phi=0.5,
                                                      rel_size_central_vote=0.7),
        lambda num_voters, num_candidates: noise(num_voters, num_candidates, phi=0.5,
                                                 rel_size_central_vote=0.7),
    )