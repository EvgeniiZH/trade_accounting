from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from trades.models import Item, Calculation, CalculationItem


User = get_user_model()


class BaseViewTestCase(TestCase):
    password = "pass12345"

    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin",
            email="admin@example.com",
            password=self.password,
            is_admin=True,
        )
        self.user = User.objects.create_user(
            username="user",
            email="user@example.com",
            password=self.password,
            is_admin=False,
        )
        self.client.force_login(self.admin)


class ItemListViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.apple = Item.objects.create(name="Apple Turbo Fan", price=Decimal("10.00"))
        self.banana = Item.objects.create(name="Banana Board", price=Decimal("20.00"))

    def test_search_filters_items(self):
        response = self.client.get(reverse("item_list"), {"search": "apple"})
        self.assertContains(response, "Apple Turbo Fan")
        self.assertNotContains(response, "Banana Board")

    def test_ajax_request_returns_partial(self):
        response = self.client.get(
            reverse("item_list"),
            {"search": "banana"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "trades/includes/item_list_content.html")
        self.assertContains(response, "Banana Board")


class CreateCalculationViewTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.alpha = Item.objects.create(name="Alpha Widget", price=Decimal("50.00"))
        self.bravo = Item.objects.create(name="Bravo Widget", price=Decimal("75.00"))

    def test_search_query_passed_to_context(self):
        response = self.client.get(reverse("create_calculation"), {"search": "alpha"})
        self.assertContains(response, "Alpha Widget")
        self.assertNotContains(response, "Bravo Widget")
        self.assertEqual(response.context["search_query"], "alpha")

    def test_ajax_partial_for_create_calculation(self):
        response = self.client.get(
            reverse("create_calculation"),
            {"search": "bravo"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "trades/includes/create_calculation_content.html"
        )
        self.assertContains(response, "Bravo Widget")


class ManageUsersPermissionTests(BaseViewTestCase):
    def test_admin_can_access_manage_users(self):
        response = self.client.get(reverse("manage_users"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Управление пользователями")

    def test_non_admin_gets_403(self):
        self.client.logout()
        self.client.force_login(self.user)
        response = self.client.get(reverse("manage_users"))
        self.assertEqual(response.status_code, 403)


class CalculationDetailSearchTests(BaseViewTestCase):
    def setUp(self):
        super().setUp()
        self.item_one = Item.objects.create(name="Rotor 1000", price=Decimal("15.00"))
        self.item_two = Item.objects.create(name="Rotor 2000", price=Decimal("25.00"))
        self.calc = Calculation.objects.create(
            title="Demo Calc", user=self.admin, markup=Decimal("10.00")
        )
        CalculationItem.objects.create(
            calculation=self.calc, item=self.item_one, quantity=1
        )

    def test_search_filter_in_edit_view(self):
        url = reverse("calculation_detail", args=[self.calc.id])
        response = self.client.get(url, {"search": "2000"})
        self.assertContains(response, "Rotor 2000")
        self.assertNotContains(response, "Rotor 1000")

