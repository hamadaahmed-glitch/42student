/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   test_ft_memcpy.c                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: cadet <cadet@42.fr>                        +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/09/26 12:10:00 by cadet             #+#    #+#             */
/*   Updated: 2026/09/26 12:10:00 by cadet            ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "student42_assert.h"
#include <stddef.h>

/* Declaration of student function */
void *ft_memcpy(void *dst, const void *src, size_t n);

int main(void)
{
	setup_signal_traps();

	TEST_START("Basic Copy")
		char src[] = "123456789";
		char dst[10] = {0};
		void *ret = ft_memcpy(dst, src, 5);
		ASSERT_TRUE(ret == dst, "ft_memcpy returns dst pointer");
		ASSERT_STR_EQ(dst, "12345", "ft_memcpy accurately transfers 5 bytes");
	TEST_END();

	TEST_START("Zero Length Transfer")
		char src[] = "abcdef";
		char dst[] = "uvwxyz";
		ft_memcpy(dst, src, 0);
		ASSERT_STR_EQ(dst, "uvwxyz", "ft_memcpy with n=0 makes no modifications");
	TEST_END();

	TEST_START("Null Pointers Protection")
		void *ret = ft_memcpy(NULL, NULL, 5);
		ASSERT_TRUE(ret == NULL, "ft_memcpy returns NULL when both dst and src are NULL");
	TEST_END();

	TEST_SUMMARY();
	return (0);
}