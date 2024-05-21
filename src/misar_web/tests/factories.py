import factory
from members.models import Member


class MemberFactory(factory.StubFactory):
    class Meta:
        model = Member

    first_name = factory.Sequence(lambda n: f"john{n}")
    last_name = factory.Sequence(lambda n: f"doe{n}")
    email = factory.Sequence(lambda n: f"john{n}@doe.com")
    phone_number = factory.Sequence(lambda n: f"123456789{n}")
    address = factory.Sequence(lambda n: f"{n} main street")
    city = factory.Sequence(lambda n: f"city{n}")
    zip_code = factory.Sequence(lambda n: f"1234{n}")
    date_of_birth = factory.Sequence(lambda n: f"2020-01-0{n}")

    @factory.post_generation
    def has_default_groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            default_group, _ = Group.objects.get_or_create(name="group")
            self.groups.add(default_group)
